from sqlmodel import SQLModel


class PackCreate(SQLModel):
    pack_name: str
    start_ep: int
    end_ep: int


class PackAdminPublic(SQLModel):
    pack_id: int
    season_id: int
    # What POST /admin/content/{content_id}/links expects.
    content_id: int
    pack_name: str
    start_ep: int
    end_ep: int


class PackListPublic(SQLModel):
    data: list[PackAdminPublic]
