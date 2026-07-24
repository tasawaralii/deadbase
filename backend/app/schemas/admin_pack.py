from sqlmodel import SQLModel


class PackCreate(SQLModel):
    pack_name: str
    start_ep: int
    end_ep: int


class PackUpdate(SQLModel):
    pack_name: str | None = None
    start_ep: int | None = None
    end_ep: int | None = None


class PackAdminPublic(SQLModel):
    pack_id: int
    season_id: int
    # What POST /admin/content/{content_id}/links expects.
    content_id: int
    pack_name: str
    start_ep: int
    end_ep: int
    link_count: int


class PackListPublic(SQLModel):
    data: list[PackAdminPublic]
