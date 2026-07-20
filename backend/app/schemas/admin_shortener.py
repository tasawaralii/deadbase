from sqlmodel import SQLModel


class ShortenerCreate(SQLModel):
    name: str
    slug: str
    api_url_template: str
    quick_url_template: str
    how_to_video_url: str | None = None
    message: str | None = None
    logo_url: str | None = None
    is_enabled: bool = True
    sort_order: int = 0


class ShortenerUpdate(SQLModel):
    name: str | None = None
    slug: str | None = None
    api_url_template: str | None = None
    quick_url_template: str | None = None
    how_to_video_url: str | None = None
    message: str | None = None
    logo_url: str | None = None
    is_enabled: bool | None = None
    sort_order: int | None = None


class ShortenerAdminPublic(SQLModel):
    id: int
    name: str
    slug: str
    api_url_template: str
    quick_url_template: str
    how_to_video_url: str | None
    message: str | None
    logo_url: str | None
    is_enabled: bool
    sort_order: int


class ShortenerAdminListPublic(SQLModel):
    data: list[ShortenerAdminPublic]
