from sqlmodel import SQLModel


class UploadQueueFailedSample(SQLModel):
    link_id: int
    attempt_count: int
    last_error: str | None


class UploadQueueStats(SQLModel):
    upload_enabled: bool
    pending: int
    success: int
    failed: int
    failed_sample: list[UploadQueueFailedSample]


class ProcessBatchRequest(SQLModel):
    limit: int = 1


class ProcessBatchResult(SQLModel):
    processed: int
    succeeded: int
    failed: int


class LinkServerJobPublic(SQLModel):
    ser_link_id: int
    link_id: int
    server_id: int
    status: str
    slug: str | None
    attempt_count: int
    last_error: str | None
