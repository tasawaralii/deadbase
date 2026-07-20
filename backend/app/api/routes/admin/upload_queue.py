from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import SessionDep, get_current_active_superuser
from app.link_upload import get_queue_stats, process_one, process_queue
from app.schemas.admin_upload_queue import (
    LinkServerJobPublic,
    ProcessBatchRequest,
    ProcessBatchResult,
    UploadQueueStats,
)

# Admin visibility/control over the background upload pipeline
# (app.link_upload) - check queue depth, manually process a batch (e.g.
# "test a few files"), or force one specific link through immediately
# regardless of queue order. Superuser-only, same as the rest of /admin.
router = APIRouter(
    prefix="/upload-queue",
    tags=["admin"],
    dependencies=[Depends(get_current_active_superuser)],
)


@router.get("/{server_sid}")
def read_queue_stats(session: SessionDep, server_sid: str) -> UploadQueueStats:
    try:
        return get_queue_stats(session, server_sid)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{server_sid}/process")
def process_batch(
    session: SessionDep, server_sid: str, body: ProcessBatchRequest
) -> ProcessBatchResult:
    result = process_queue(session, server_sid, body.limit, force=True)
    return ProcessBatchResult(**result)


@router.post("/{server_sid}/links/{link_id}")
def upload_link_now(session: SessionDep, server_sid: str, link_id: int) -> LinkServerJobPublic:
    try:
        job = process_one(session, server_sid, link_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return LinkServerJobPublic(
        ser_link_id=job.ser_link_id,
        link_id=job.link_id,
        server_id=job.server_id,
        status=job.status.value,
        slug=job.slug,
        attempt_count=job.attempt_count,
        last_error=job.last_error,
    )
