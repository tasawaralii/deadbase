"""
Scheduled job: folds newly recorded download events into the content daily
rollup table, prunes rolled-up raw rows past their retention window, then
compacts daily rows older than DAILY_RETENTION_DAYS into the monthly table.
Meant to run every 10-30 minutes via cron/systemd timer - safe to run more
or less often, or to skip a run entirely. Server/shortener stats aren't
touched here - those are incremented inline at write time (see
app.download_stats), never batched.
"""

from sqlmodel import Session

from app.core.db import engine
from app.download_stats import (
    compact_old_daily_downloads,
    prune_old_download_events,
    rollup_content_downloads,
)

if __name__ == "__main__":
    with Session(engine) as session:
        rolled_up = rollup_content_downloads(session)
        pruned = prune_old_download_events(session)
        compacted = compact_old_daily_downloads(session)
        print(  # noqa: T201
            f"rolled up {rolled_up} download(s), pruned {pruned} old row(s), "
            f"compacted {compacted} daily row(s) into monthly"
        )
