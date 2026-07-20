import uuid
from datetime import UTC, date, datetime, timedelta
from typing import Literal

from sqlalchemy import union_all
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import selectinload
from sqlmodel import Session, col, func, select

from app.content import get_playable_content
from app.media import resolve_image_urls
from app.models import (
    Animes,
    AnimeViewDaily,
    AnimeViewMonthly,
    Content,
    ContentContentType,
    ContentViewDaily,
    ContentViewMonthly,
    ContentViews,
    Episodes,
    Seasons,
    SeasonViewDaily,
    SeasonViewMonthly,
)
from app.schemas.anime import AnimeSummary
from app.schemas.trending import TrendingAnimeItem, TrendingAnimeList

TrendingWindow = Literal["today", "week", "month", "all"]

WINDOW_DAYS: dict[str, int | None] = {"today": 0, "week": 7, "month": 30, "all": None}

VIEW_ROW_RETENTION = timedelta(days=2)

# How long a *ViewDaily row survives before being folded into the matching
# *ViewMonthly row and deleted - full daily granularity for a rolling recent
# window, coarser monthly totals for the long tail of history. Same constant
# name/value as app.download_stats.DAILY_RETENTION_DAYS, deliberately - both
# pipelines follow the identical tiering strategy.
DAILY_RETENTION_DAYS = 30


def record_view(session: Session, visitor_id: uuid.UUID, content_id: int) -> None:
    if not get_playable_content(session, content_id):
        raise ValueError("Content is not trackable")

    stmt = (
        pg_insert(ContentViews)
        .values(
            visitor_id=visitor_id,
            content_id=content_id,
            view_date=datetime.now(UTC).date(),
        )
        .on_conflict_do_nothing(
            index_elements=["visitor_id", "content_id", "view_date"]
        )
    )
    session.execute(stmt)
    session.commit()


def _resolve_hierarchy(session: Session, content_id: int) -> tuple[int | None, int] | None:
    """Returns (season_id, anime_id). season_id is None for movies."""
    content = session.get(Content, content_id)
    if not content:
        return None

    if content.content_type == ContentContentType.MOVIE:
        anime_id = session.exec(
            select(Animes.anime_id).where(Animes.content_id == content_id)
        ).first()
        return None if anime_id is None else (None, anime_id)

    if content.content_type == ContentContentType.EPISODE:
        row = session.exec(
            select(Episodes.season_id, Seasons.anime_id)
            .join(Seasons, col(Seasons.season_id) == Episodes.season_id)
            .where(Episodes.content_id == content_id)
        ).first()
        return None if row is None else (row[0], row[1])

    return None


def _bump_content_daily(
    session: Session, content_id: int, view_date: date, count: int
) -> None:
    row = session.exec(
        select(ContentViewDaily).where(
            ContentViewDaily.content_id == content_id,
            ContentViewDaily.view_date == view_date,
        )
    ).first()
    if row:
        row.view_count += count
    else:
        row = ContentViewDaily(
            content_id=content_id, view_date=view_date, view_count=count
        )
    session.add(row)


def _bump_season_daily(
    session: Session, season_id: int, view_date: date, count: int
) -> None:
    row = session.exec(
        select(SeasonViewDaily).where(
            SeasonViewDaily.season_id == season_id,
            SeasonViewDaily.view_date == view_date,
        )
    ).first()
    if row:
        row.view_count += count
    else:
        row = SeasonViewDaily(
            season_id=season_id, view_date=view_date, view_count=count
        )
    session.add(row)


def _bump_anime_daily(
    session: Session, anime_id: int, view_date: date, count: int
) -> None:
    row = session.exec(
        select(AnimeViewDaily).where(
            AnimeViewDaily.anime_id == anime_id,
            AnimeViewDaily.view_date == view_date,
        )
    ).first()
    if row:
        row.view_count += count
    else:
        row = AnimeViewDaily(anime_id=anime_id, view_date=view_date, view_count=count)
    session.add(row)


def rollup_views(session: Session) -> int:
    """
    Folds newly recorded, not-yet-rolled-up views into the content/season/anime
    daily rollup tables. Safe to run repeatedly on a schedule (e.g. every
    10-30 min) - only touches rows with rolled_up=False.
    """
    pending = session.exec(
        select(ContentViews).where(col(ContentViews.rolled_up) == False)  # noqa: E712
    ).all()
    if not pending:
        return 0

    by_content_date: dict[tuple[int, date], int] = {}
    for row in pending:
        key = (row.content_id, row.view_date)
        by_content_date[key] = by_content_date.get(key, 0) + 1

    season_totals: dict[tuple[int, date], int] = {}
    anime_totals: dict[tuple[int, date], int] = {}

    for (content_id, view_date), count in by_content_date.items():
        _bump_content_daily(session, content_id, view_date, count)

        hierarchy = _resolve_hierarchy(session, content_id)
        if hierarchy is None:
            continue
        season_id, anime_id = hierarchy
        if season_id is not None:
            key = (season_id, view_date)
            season_totals[key] = season_totals.get(key, 0) + count
        key = (anime_id, view_date)
        anime_totals[key] = anime_totals.get(key, 0) + count

    for (season_id, view_date), count in season_totals.items():
        _bump_season_daily(session, season_id, view_date, count)
    for (anime_id, view_date), count in anime_totals.items():
        _bump_anime_daily(session, anime_id, view_date, count)

    for row in pending:
        row.rolled_up = True
        session.add(row)

    session.commit()
    return len(pending)


def prune_old_views(session: Session) -> int:
    """Deletes rolled-up dedup rows once their day is over and dedup no longer matters."""
    cutoff = datetime.now(UTC).date() - VIEW_ROW_RETENTION
    old_rows = session.exec(
        select(ContentViews).where(
            col(ContentViews.rolled_up) == True,  # noqa: E712
            ContentViews.view_date < cutoff,
        )
    ).all()
    for row in old_rows:
        session.delete(row)
    session.commit()
    return len(old_rows)


def _daily_retention_cutoff() -> date:
    return datetime.now(UTC).date() - timedelta(days=DAILY_RETENTION_DAYS)


def compact_old_content_view_daily(session: Session) -> int:
    """Folds ContentViewDaily rows older than DAILY_RETENTION_DAYS into ContentViewMonthly."""
    cutoff = _daily_retention_cutoff()
    old_rows = session.exec(
        select(ContentViewDaily).where(ContentViewDaily.view_date < cutoff)
    ).all()
    if not old_rows:
        return 0

    totals: dict[tuple[int, int, int], int] = {}
    for row in old_rows:
        key = (row.content_id, row.view_date.year, row.view_date.month)
        totals[key] = totals.get(key, 0) + row.view_count

    for (content_id, year, month), count in totals.items():
        monthly = session.exec(
            select(ContentViewMonthly).where(
                ContentViewMonthly.content_id == content_id,
                ContentViewMonthly.year == year,
                ContentViewMonthly.month == month,
            )
        ).first()
        if monthly:
            monthly.view_count += count
        else:
            monthly = ContentViewMonthly(
                content_id=content_id, year=year, month=month, view_count=count
            )
        session.add(monthly)

    for row in old_rows:
        session.delete(row)

    session.commit()
    return len(old_rows)


def compact_old_season_view_daily(session: Session) -> int:
    """Folds SeasonViewDaily rows older than DAILY_RETENTION_DAYS into SeasonViewMonthly."""
    cutoff = _daily_retention_cutoff()
    old_rows = session.exec(
        select(SeasonViewDaily).where(SeasonViewDaily.view_date < cutoff)
    ).all()
    if not old_rows:
        return 0

    totals: dict[tuple[int, int, int], int] = {}
    for row in old_rows:
        key = (row.season_id, row.view_date.year, row.view_date.month)
        totals[key] = totals.get(key, 0) + row.view_count

    for (season_id, year, month), count in totals.items():
        monthly = session.exec(
            select(SeasonViewMonthly).where(
                SeasonViewMonthly.season_id == season_id,
                SeasonViewMonthly.year == year,
                SeasonViewMonthly.month == month,
            )
        ).first()
        if monthly:
            monthly.view_count += count
        else:
            monthly = SeasonViewMonthly(
                season_id=season_id, year=year, month=month, view_count=count
            )
        session.add(monthly)

    for row in old_rows:
        session.delete(row)

    session.commit()
    return len(old_rows)


def compact_old_anime_view_daily(session: Session) -> int:
    """Folds AnimeViewDaily rows older than DAILY_RETENTION_DAYS into AnimeViewMonthly."""
    cutoff = _daily_retention_cutoff()
    old_rows = session.exec(
        select(AnimeViewDaily).where(AnimeViewDaily.view_date < cutoff)
    ).all()
    if not old_rows:
        return 0

    totals: dict[tuple[int, int, int], int] = {}
    for row in old_rows:
        key = (row.anime_id, row.view_date.year, row.view_date.month)
        totals[key] = totals.get(key, 0) + row.view_count

    for (anime_id, year, month), count in totals.items():
        monthly = session.exec(
            select(AnimeViewMonthly).where(
                AnimeViewMonthly.anime_id == anime_id,
                AnimeViewMonthly.year == year,
                AnimeViewMonthly.month == month,
            )
        ).first()
        if monthly:
            monthly.view_count += count
        else:
            monthly = AnimeViewMonthly(
                anime_id=anime_id, year=year, month=month, view_count=count
            )
        session.add(monthly)

    for row in old_rows:
        session.delete(row)

    session.commit()
    return len(old_rows)


def window_cutoff(window: TrendingWindow) -> date | None:
    days = WINDOW_DAYS[window]
    if days is None:
        return None
    return datetime.now(UTC).date() - timedelta(days=days)


def get_trending_anime(
    session: Session, window: TrendingWindow, limit: int
) -> list[tuple[Animes, int]]:
    if window == "all":
        combined = union_all(
            select(
                col(AnimeViewDaily.anime_id).label("anime_id"),
                col(AnimeViewDaily.view_count).label("view_count"),
            ),
            select(
                col(AnimeViewMonthly.anime_id).label("anime_id"),
                col(AnimeViewMonthly.view_count).label("view_count"),
            ),
        ).subquery()
        views_subq = (
            select(combined.c.anime_id, func.sum(combined.c.view_count).label("views"))
            .group_by(combined.c.anime_id)
            .subquery()
        )
    else:
        cutoff = window_cutoff(window)
        assert cutoff is not None  # only "all" (handled above) yields None
        views_subq = (
            select(
                AnimeViewDaily.anime_id, func.sum(AnimeViewDaily.view_count).label("views")
            )
            .where(AnimeViewDaily.view_date >= cutoff)
            .group_by(col(AnimeViewDaily.anime_id))
            .subquery()
        )

    rows = session.exec(
        select(Animes, views_subq.c.views)
        .join(views_subq, views_subq.c.anime_id == Animes.anime_id)
        .options(
            selectinload(Animes.age),  # type: ignore[arg-type]
            selectinload(Animes.genre),  # type: ignore[arg-type]
        )
        .order_by(col(views_subq.c.views).desc())
        .limit(limit)
    ).all()
    return list(rows)


def build_trending_anime_list(
    session: Session, window: TrendingWindow, limit: int
) -> TrendingAnimeList:
    """
    Shared response-builder for `get_trending_anime` - used by both the
    public trending endpoint and the admin stats views endpoint so the two
    don't drift out of sync with two copies of the same mapping.
    """
    rows = get_trending_anime(session, window, limit)

    data = []
    for anime, views in rows:
        season_count = None
        if anime.type != "movie":
            season_count = session.exec(
                select(func.count(col(Seasons.season_id))).where(
                    Seasons.anime_id == anime.anime_id
                )
            ).one()
        data.append(
            TrendingAnimeItem(
                anime=AnimeSummary(
                    slug=anime.slug,
                    anime_name=anime.anime_name,
                    type=anime.type,
                    poster=resolve_image_urls(
                        anime.poster_source, anime.poster_img, "poster"
                    ),
                    rating=anime.rating,
                    age_rating=anime.age.age_name,
                    genres=[g.genre_name for g in anime.genre],
                    season_count=season_count,
                ),
                views=views,
            )
        )
    return TrendingAnimeList(data=data)


def get_trending_seasons(
    session: Session, window: TrendingWindow, limit: int
) -> list[tuple[Seasons, int]]:
    if window == "all":
        combined = union_all(
            select(
                col(SeasonViewDaily.season_id).label("season_id"),
                col(SeasonViewDaily.view_count).label("view_count"),
            ),
            select(
                col(SeasonViewMonthly.season_id).label("season_id"),
                col(SeasonViewMonthly.view_count).label("view_count"),
            ),
        ).subquery()
        views_subq = (
            select(combined.c.season_id, func.sum(combined.c.view_count).label("views"))
            .group_by(combined.c.season_id)
            .subquery()
        )
    else:
        cutoff = window_cutoff(window)
        assert cutoff is not None  # only "all" (handled above) yields None
        views_subq = (
            select(
                SeasonViewDaily.season_id,
                func.sum(SeasonViewDaily.view_count).label("views"),
            )
            .where(SeasonViewDaily.view_date >= cutoff)
            .group_by(col(SeasonViewDaily.season_id))
            .subquery()
        )

    rows = session.exec(
        select(Seasons, views_subq.c.views)
        .join(views_subq, views_subq.c.season_id == Seasons.season_id)
        .options(selectinload(Seasons.anime))  # type: ignore[arg-type]
        .order_by(col(views_subq.c.views).desc())
        .limit(limit)
    ).all()
    return list(rows)


def get_trending_episodes(
    session: Session, window: TrendingWindow, limit: int
) -> list[tuple[Episodes, int]]:
    if window == "all":
        combined = union_all(
            select(
                col(ContentViewDaily.content_id).label("content_id"),
                col(ContentViewDaily.view_count).label("view_count"),
            ),
            select(
                col(ContentViewMonthly.content_id).label("content_id"),
                col(ContentViewMonthly.view_count).label("view_count"),
            ),
        ).subquery()
        views_subq = (
            select(combined.c.content_id, func.sum(combined.c.view_count).label("views"))
            .group_by(combined.c.content_id)
            .subquery()
        )
    else:
        cutoff = window_cutoff(window)
        assert cutoff is not None  # only "all" (handled above) yields None
        views_subq = (
            select(
                ContentViewDaily.content_id,
                func.sum(ContentViewDaily.view_count).label("views"),
            )
            .where(ContentViewDaily.view_date >= cutoff)
            .group_by(col(ContentViewDaily.content_id))
            .subquery()
        )

    rows = session.exec(
        select(Episodes, views_subq.c.views)
        .join(views_subq, views_subq.c.content_id == Episodes.content_id)
        .options(
            selectinload(Episodes.season).selectinload(Seasons.anime)  # type: ignore[arg-type]
        )
        .order_by(col(views_subq.c.views).desc())
        .limit(limit)
    ).all()
    return list(rows)
