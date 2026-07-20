from sqlmodel import SQLModel


class OttPlatformCreate(SQLModel):
    ott_sid: str
    ott_name: str


class OttPlatformUpdate(SQLModel):
    ott_sid: str | None = None
    ott_name: str | None = None


class OttPlatformAdminPublic(SQLModel):
    ott_id: int
    ott_sid: str
    ott_name: str


class OttPlatformAdminListPublic(SQLModel):
    data: list[OttPlatformAdminPublic]
