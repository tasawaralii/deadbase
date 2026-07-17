"""
Scheduled job: folds newly recorded content views into the daily rollup
tables, then prunes dedup rows whose day is over. Meant to run every
10-30 minutes via cron/systemd timer - safe to run more or less often,
or to skip a run entirely.
"""

from sqlmodel import Session

from app.core.db import engine
from app.trending import prune_old_views, rollup_views

if __name__ == "__main__":
    with Session(engine) as session:
        rolled_up = rollup_views(session)
        pruned = prune_old_views(session)
        print(f"rolled up {rolled_up} view(s), pruned {pruned} old row(s)")  # noqa: T201
