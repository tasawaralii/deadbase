"""
Background upload pipeline: mirrors gdrive-hosted links onto third-party
file-host servers (FilePress etc, see app/uploaders/) and records the
result on LinkServers so resolved links start showing up publicly (see
app.media.build_download_links, which already skips any row without a
slug - a pending/failed job is invisible there with zero extra code).

Job state lives directly on LinkServers rather than a separate queue table
- a row IS the job. status=PENDING covers both "never attempted" and
"waiting to retry" (next_attempt_at governs which); status=FAILED is a
terminal dead-letter state (non-retryable error, or attempts exhausted) -
excluded from the automatic queue, left for a human to look at (or force
via process_one). status=SUCCESS means done, slug is real.

ServerInfo.upload_enabled is the admin start/stop switch for the
*automatic* pipeline (cron-driven ensure_queued/process_queue) - separate
from is_enabled, which gates public visibility of already-uploaded links.
Manual admin actions (process_queue(force=True), process_one) always
bypass it, since pausing "don't auto-upload everything" shouldn't also
block "let me manually test/prioritize this one link."
"""

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, or_
from sqlmodel import Session, col, select

from app.models import Links, LinkServers, LinkServerStatus, ServerInfo
from app.schemas.admin_upload_queue import UploadQueueFailedSample, UploadQueueStats
from app.uploaders import UPLOADERS, UploadError

MAX_ATTEMPTS = 3
# Wait before attempt 2, wait before attempt 3 - one fewer entry than
# MAX_ATTEMPTS since the last attempt's failure is terminal, not scheduled.
BACKOFF_MINUTES = [5, 15]


def ensure_queued(session: Session, server_sid: str) -> int:
    """
    Creates a pending LinkServers row for every live Link that doesn't yet
    have one for this server. Cheap to run every cycle - only touches links
    with no row at all for this server, which shrinks to ~0 once caught up.
    Always runs regardless of upload_enabled - it's just bookkeeping (no
    external calls), and keeps the queue visible for admin inspection even
    while the automatic pipeline is paused.
    """
    server = session.exec(
        select(ServerInfo).where(ServerInfo.server_sid == server_sid)
    ).first()
    if server is None:
        return 0

    already_queued = select(LinkServers.link_id).where(
        LinkServers.server_id == server.server_id
    )
    missing_link_ids = session.exec(
        select(Links.link_id)
        .where(col(Links.is_live) == True)  # noqa: E712
        .where(col(Links.link_id).not_in(already_queued))
    ).all()

    for link_id in missing_link_ids:
        session.add(
            LinkServers(
                link_id=link_id, server_id=server.server_id, status=LinkServerStatus.PENDING
            )
        )
    if missing_link_ids:
        session.commit()
    return len(missing_link_ids)


def _backoff_delay(attempt_count: int) -> timedelta:
    index = min(attempt_count - 1, len(BACKOFF_MINUTES) - 1)
    return timedelta(minutes=BACKOFF_MINUTES[index])


def _attempt(server: ServerInfo, job: LinkServers, link: Links) -> bool:
    """Calls the uploader once, mutates job in place, returns True on success."""
    uploader = UPLOADERS[server.server_sid]
    now = datetime.now(UTC)
    job.attempt_count += 1
    job.last_attempted_at = now

    try:
        slug = uploader(server, link.gdriveid)
    except UploadError as exc:
        job.last_error = str(exc)[:500]
        if not exc.retryable or job.attempt_count >= MAX_ATTEMPTS:
            job.status = LinkServerStatus.FAILED
            job.next_attempt_at = None
        else:
            job.next_attempt_at = now + _backoff_delay(job.attempt_count)
        return False
    else:
        job.status = LinkServerStatus.SUCCESS
        job.slug = slug
        job.last_error = None
        job.next_attempt_at = None
        return True


def process_queue(
    session: Session, server_sid: str, batch_size: int, *, force: bool = False
) -> dict[str, int]:
    """
    Processes up to batch_size due jobs for one server: calls the matching
    uploader, records success/failure with backoff. Never raises - a bad
    job is recorded as failed and the loop moves on to the next one.
    Respects ServerInfo.upload_enabled unless force=True (admin-triggered
    manual batch, e.g. "test a few files").
    """
    uploader = UPLOADERS.get(server_sid)
    if uploader is None:
        return {"processed": 0, "succeeded": 0, "failed": 0}

    server = session.exec(
        select(ServerInfo).where(ServerInfo.server_sid == server_sid)
    ).first()
    if server is None or (not force and not server.upload_enabled):
        return {"processed": 0, "succeeded": 0, "failed": 0}

    now = datetime.now(UTC)
    jobs = session.exec(
        select(LinkServers)
        .where(
            LinkServers.server_id == server.server_id,
            LinkServers.status == LinkServerStatus.PENDING,
            or_(
                col(LinkServers.next_attempt_at).is_(None),
                col(LinkServers.next_attempt_at) <= now,
            ),
        )
        .order_by(col(LinkServers.link_id).desc())
        .limit(batch_size)
    ).all()

    succeeded = 0
    failed = 0
    for job in jobs:
        link = session.get(Links, job.link_id)
        if link is None:
            # Orphaned job (link deleted since being queued) - nothing to upload.
            session.delete(job)
            session.commit()
            continue

        if _attempt(server, job, link):
            succeeded += 1
        else:
            failed += 1

        session.add(job)
        session.commit()

    return {"processed": len(jobs), "succeeded": succeeded, "failed": failed}


def process_one(session: Session, server_sid: str, link_id: int) -> LinkServers:
    """
    Uploads one specific link to one specific server right now - ignores
    upload_enabled, next_attempt_at/backoff timing, and MAX_ATTEMPTS entirely
    (an explicit admin action, not the automatic queue). Creates the
    LinkServers row if it doesn't exist yet. Raises ValueError if the
    server/link/uploader don't exist - the caller (an admin route) turns
    that into a 404.
    """
    uploader = UPLOADERS.get(server_sid)
    if uploader is None:
        raise ValueError(f"No uploader registered for server '{server_sid}'")

    server = session.exec(
        select(ServerInfo).where(ServerInfo.server_sid == server_sid)
    ).first()
    if server is None:
        raise ValueError(f"No server with sid '{server_sid}'")

    link = session.get(Links, link_id)
    if link is None:
        raise ValueError(f"No link with id {link_id}")

    job = session.exec(
        select(LinkServers).where(
            LinkServers.server_id == server.server_id, LinkServers.link_id == link_id
        )
    ).first()
    if job is None:
        job = LinkServers(
            link_id=link_id, server_id=server.server_id, status=LinkServerStatus.PENDING
        )

    _attempt(server, job, link)

    session.add(job)
    session.commit()
    session.refresh(job)
    return job


def get_queue_stats(session: Session, server_sid: str) -> UploadQueueStats:
    """Queue depth + a sample of failed jobs, for admin visibility."""
    server = session.exec(
        select(ServerInfo).where(ServerInfo.server_sid == server_sid)
    ).first()
    if server is None:
        raise ValueError(f"No server with sid '{server_sid}'")

    def count(status: LinkServerStatus) -> int:
        return session.exec(
            select(func.count())
            .select_from(LinkServers)
            .where(LinkServers.server_id == server.server_id, LinkServers.status == status)
        ).one()

    failed_sample = session.exec(
        select(LinkServers)
        .where(
            LinkServers.server_id == server.server_id,
            LinkServers.status == LinkServerStatus.FAILED,
        )
        .order_by(col(LinkServers.last_attempted_at).desc())
        .limit(10)
    ).all()

    return UploadQueueStats(
        upload_enabled=server.upload_enabled,
        pending=count(LinkServerStatus.PENDING),
        success=count(LinkServerStatus.SUCCESS),
        failed=count(LinkServerStatus.FAILED),
        failed_sample=[
            UploadQueueFailedSample(
                link_id=j.link_id, attempt_count=j.attempt_count, last_error=j.last_error
            )
            for j in failed_sample
        ],
    )
