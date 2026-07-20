"""
Scheduled job: for every registered uploader (see app/uploaders/), queues
any live link not yet attempted for that server, then processes one due
job per server (new/never-attempted or scheduled for retry). Meant to run
every minute via cron - deliberately slow/conservative since these are
external third-party APIs with their own rate limits; raise BATCH_SIZE
once real-world behavior is confirmed safe to go faster.
"""

from sqlmodel import Session

from app.core.db import engine
from app.link_upload import ensure_queued, process_queue
from app.uploaders import UPLOADERS

BATCH_SIZE = 1

if __name__ == "__main__":
    with Session(engine) as session:
        for server_sid in UPLOADERS:
            queued = ensure_queued(session, server_sid)
            result = process_queue(session, server_sid, BATCH_SIZE)
            print(  # noqa: T201
                f"{server_sid}: queued {queued} new, processed {result['processed']} "
                f"({result['succeeded']} succeeded, {result['failed']} failed)"
            )
