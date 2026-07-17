import uuid
from datetime import UTC, date, datetime, timedelta
from typing import Literal

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import selectinload
from sqlmodel import Session, col, func, select

from app.content import get_playable_content
from app.models import (
    Animes,
    AnimeViewDaily,
    Content,
    ContentContentType,
    ContentViewDaily,
    ContentViews,
    Episodes,
    Seasons,
    SeasonViewDaily,
)

TrendingWindow = Literal["today", "week", "month", "all"]

WINDOW_DAYS: dict[str, int | None] = {"today": 0, "week": 7, "month": 30, "all": None}

VIEW_ROW_RETENTION = timedelta(days=2)


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


def _window_cutoff(window: TrendingWindow) -> date | None:
    days = WINDOW_DAYS[window]
    if days is None:
        return None
    return datetime.now(UTC).date() - timedelta(days=days)


def get_trending_anime(
    session: Session, window: TrendingWindow, limit: int
) -> list[tuple[Animes, int]]:
    cutoff = _window_cutoff(window)
    views_query = select(
        AnimeViewDaily.anime_id, func.sum(AnimeViewDaily.view_count).label("views")
    )
    if cutoff is not None:
        views_query = views_query.where(AnimeViewDaily.view_date >= cutoff)
    views_subq = views_query.group_by(col(AnimeViewDaily.anime_id)).subquery()

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


def get_trending_seasons(
    session: Session, window: TrendingWindow, limit: int
) -> list[tuple[Seasons, int]]:
    cutoff = _window_cutoff(window)
    views_query = select(
        SeasonViewDaily.season_id, func.sum(SeasonViewDaily.view_count).label("views")
    )
    if cutoff is not None:
        views_query = views_query.where(SeasonViewDaily.view_date >= cutoff)
    views_subq = views_query.group_by(col(SeasonViewDaily.season_id)).subquery()

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
    cutoff = _window_cutoff(window)
    views_query = select(
        ContentViewDaily.content_id,
        func.sum(ContentViewDaily.view_count).label("views"),
    )
    if cutoff is not None:
        views_query = views_query.where(ContentViewDaily.view_date >= cutoff)
    views_subq = views_query.group_by(col(ContentViewDaily.content_id)).subquery()

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
