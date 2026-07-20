"""
Scheduled job: folds newly recorded content views into the daily rollup
tables, prunes dedup rows whose day is over, then compacts daily rows older
than DAILY_RETENTION_DAYS into the monthly tables. Meant to run every 10-30
minutes via cron/systemd timer - safe to run more or less often, or to skip
a run entirely.
"""

from sqlmodel import Session

from app.core.db import engine
from app.trending import (
    compact_old_anime_view_daily,
    compact_old_content_view_daily,
    compact_old_season_view_daily,
    prune_old_views,
    rollup_views,
)

if __name__ == "__main__":
    with Session(engine) as session:
        rolled_up = rollup_views(session)
        pruned = prune_old_views(session)
        compacted = (
            compact_old_content_view_daily(session)
            + compact_old_season_view_daily(session)
            + compact_old_anime_view_daily(session)
        )
        print(  # noqa: T201
            f"rolled up {rolled_up} view(s), pruned {pruned} old row(s), "
            f"compacted {compacted} daily row(s) into monthly"
        )
