from sqlmodel import SQLModel


class ShortenerOption(SQLModel):
    id: int
    name: str
    message: str | None
    how_to_video_url: str | None
    logo_url: str | None
    already_solved: bool
    reported: bool


class UnlockStatus(SQLModel):
    unlocked: bool
    url: str | None = None
    solved: int | None = None
    required: int | None = None
    shorteners: list[ShortenerOption] | None = None


class StartUnlockRequest(SQLModel):
    shortener_id: int


class StartUnlockResponse(SQLModel):
    redirect_url: str


class ReportRequest(SQLModel):
    shortener_id: int
    reason: str | None = None
