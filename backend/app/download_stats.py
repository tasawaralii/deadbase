"""
Download/unlock-funnel analytics, parallel to app.trending but for a
different funnel: views come from streaming (player pages), downloads come
from completing the unlock flow (shortener-solved or already-unlocked
direct access) - see app.unlock.record_download_event.

Content is high-cardinality (tens of thousands of movies/episodes/packs), so
it gets the same two-tier treatment as views: raw DownloadEvents rows are
rolled into ContentDownloadDaily (kept for a rolling DAILY_RETENTION_DAYS),
then compacted into ContentDownloadMonthly (kept forever) once older than
that - full daily granularity for a recent window, coarser monthly totals
for the long tail of history, so neither table grows without bound.

Servers and shorteners are tiny in number (4-10 each) so they skip the
monthly tier entirely: ServerDownloadDaily/ShortenerFunnelDaily are
incremented inline, atomically (via INSERT ... ON CONFLICT DO UPDATE,
since - unlike the batch rollup functions below - these run from concurrent
request handlers, not a single-threaded cron job), and just kept forever;
even years of daily rows at that cardinality is a few thousand rows.
"""

from datetime import UTC, date, datetime, timedelta

from sqlalchemy import union_all
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlmodel import Session, col, func, select

from app.models import (
    ContentDownloadDaily,
    ContentDownloadMonthly,
    DownloadEvents,
    ServerDownloadDaily,
    ShortenerFunnelDaily,
)
from app.trending import TrendingWindow, window_cutoff

DAILY_RETENTION_DAYS = 30

# Longer than ContentViews' 2-day retention - downloads are lower-frequency
# than views, and abuse/fraud investigation on the unlock flow benefits from
# more raw-row lookback than streaming views need.
RAW_EVENT_RETENTION = timedelta(days=7)


def bump_server_download_daily(session: Session, server_id: int, day: date, count: int = 1) -> None:
    stmt = pg_insert(ServerDownloadDaily).values(
        server_id=server_id, download_date=day, download_count=count
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["server_id", "download_date"],
        set_={"download_count": ServerDownloadDaily.download_count + stmt.excluded.download_count},
    )
    session.execute(stmt)


def bump_shortener_funnel_daily(
    session: Session,
    shortener_id: int,
    day: date,
    *,
    attempts: int = 0,
    solved: int = 0,
    reported: int = 0,
) -> None:
    stmt = pg_insert(ShortenerFunnelDaily).values(
        shortener_id=shortener_id,
        stat_date=day,
        attempts=attempts,
        solved=solved,
        reported=reported,
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["shortener_id", "stat_date"],
        set_={
            "attempts": ShortenerFunnelDaily.attempts + stmt.excluded.attempts,
            "solved": ShortenerFunnelDaily.solved + stmt.excluded.solved,
            "reported": ShortenerFunnelDaily.reported + stmt.excluded.reported,
        },
    )
    session.execute(stmt)


def _bump_content_download_daily(session: Session, content_id: int, day: date, count: int) -> None:
    row = session.exec(
        select(ContentDownloadDaily).where(
            ContentDownloadDaily.content_id == content_id,
            ContentDownloadDaily.download_date == day,
        )
    ).first()
    if row:
        row.download_count += count
    else:
        row = ContentDownloadDaily(content_id=content_id, download_date=day, download_count=count)
    session.add(row)


def rollup_content_downloads(session: Session) -> int:
    """
    Folds newly recorded, not-yet-rolled-up download events into
    ContentDownloadDaily. Safe to run repeatedly on a schedule. No dedup
    needed (unlike views) - every download is a distinct, meaningful event
    worth counting, not noise to collapse.
    """
    pending = session.exec(
        select(DownloadEvents).where(col(DownloadEvents.rolled_up) == False)  # noqa: E712
    ).all()
    if not pending:
        return 0

    by_content_date: dict[tuple[int, date], int] = {}
    for row in pending:
        key = (row.content_id, row.occurred_at.date())
        by_content_date[key] = by_content_date.get(key, 0) + 1

    for (content_id, download_date), count in by_content_date.items():
        _bump_content_download_daily(session, content_id, download_date, count)

    for row in pending:
        row.rolled_up = True
        session.add(row)

    session.commit()
    return len(pending)


def prune_old_download_events(session: Session) -> int:
    """Deletes rolled-up raw download events past the raw-row retention window."""
    cutoff = datetime.now(UTC) - RAW_EVENT_RETENTION
    old_rows = session.exec(
        select(DownloadEvents).where(
            col(DownloadEvents.rolled_up) == True,  # noqa: E712
            DownloadEvents.occurred_at < cutoff,
        )
    ).all()
    for row in old_rows:
        session.delete(row)
    session.commit()
    return len(old_rows)


def compact_old_daily_downloads(session: Session) -> int:
    """
    Folds ContentDownloadDaily rows older than DAILY_RETENTION_DAYS into
    ContentDownloadMonthly (one row per content_id/year/month) and deletes
    the daily rows - the "day 1..30, then month 3/month 2/month 1" tiering.
    """
    cutoff = datetime.now(UTC).date() - timedelta(days=DAILY_RETENTION_DAYS)
    old_rows = session.exec(
        select(ContentDownloadDaily).where(ContentDownloadDaily.download_date < cutoff)
    ).all()
    if not old_rows:
        return 0

    by_content_month: dict[tuple[int, int, int], int] = {}
    for row in old_rows:
        key = (row.content_id, row.download_date.year, row.download_date.month)
        by_content_month[key] = by_content_month.get(key, 0) + row.download_count

    for (content_id, year, month), count in by_content_month.items():
        monthly = session.exec(
            select(ContentDownloadMonthly).where(
                ContentDownloadMonthly.content_id == content_id,
                ContentDownloadMonthly.year == year,
                ContentDownloadMonthly.month == month,
            )
        ).first()
        if monthly:
            monthly.download_count += count
        else:
            monthly = ContentDownloadMonthly(
                content_id=content_id, year=year, month=month, download_count=count
            )
        session.add(monthly)

    for row in old_rows:
        session.delete(row)

    session.commit()
    return len(old_rows)


def get_top_content_downloads(
    session: Session, window: TrendingWindow, limit: int
) -> list[tuple[int, int]]:
    """Returns [(content_id, downloads), ...] ordered by downloads desc."""
    if window == "all":
        combined = union_all(
            select(
                col(ContentDownloadDaily.content_id).label("content_id"),
                col(ContentDownloadDaily.download_count).label("download_count"),
            ),
            select(
                col(ContentDownloadMonthly.content_id).label("content_id"),
                col(ContentDownloadMonthly.download_count).label("download_count"),
            ),
        ).subquery()
        rows = session.exec(
            select(combined.c.content_id, func.sum(combined.c.download_count).label("downloads"))
            .group_by(combined.c.content_id)
            .order_by(func.sum(combined.c.download_count).desc())
            .limit(limit)
        ).all()
        return list(rows)

    cutoff = window_cutoff(window)
    assert cutoff is not None  # only "all" (handled above) yields None
    rows = session.exec(
        select(
            ContentDownloadDaily.content_id,
            func.sum(ContentDownloadDaily.download_count).label("downloads"),
        )
        .where(ContentDownloadDaily.download_date >= cutoff)
        .group_by(col(ContentDownloadDaily.content_id))
        .order_by(func.sum(ContentDownloadDaily.download_count).desc())
        .limit(limit)
    ).all()
    return list(rows)


def get_shortener_funnel(
    session: Session, window: TrendingWindow
) -> list[tuple[int, int, int, int]]:
    """Returns [(shortener_id, attempts, solved, reported), ...]."""
    query = select(
        ShortenerFunnelDaily.shortener_id,
        func.sum(ShortenerFunnelDaily.attempts).label("attempts"),
        func.sum(ShortenerFunnelDaily.solved).label("solved"),
        func.sum(ShortenerFunnelDaily.reported).label("reported"),
    ).group_by(col(ShortenerFunnelDaily.shortener_id))
    cutoff = window_cutoff(window)
    if cutoff is not None:
        query = query.where(ShortenerFunnelDaily.stat_date >= cutoff)
    return list(session.exec(query).all())


def get_server_downloads(session: Session, window: TrendingWindow) -> list[tuple[int, int]]:
    """Returns [(server_id, downloads), ...]."""
    query = select(
        ServerDownloadDaily.server_id,
        func.sum(ServerDownloadDaily.download_count).label("downloads"),
    ).group_by(col(ServerDownloadDaily.server_id))
    cutoff = window_cutoff(window)
    if cutoff is not None:
        query = query.where(ServerDownloadDaily.download_date >= cutoff)
    return list(session.exec(query).all())
