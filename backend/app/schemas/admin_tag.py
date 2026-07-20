from sqlmodel import SQLModel


class TagCreate(SQLModel):
    slug: str
    name: str


class TagUpdate(SQLModel):
    slug: str | None = None
    name: str | None = None


class TagAdminPublic(SQLModel):
    id: int
    slug: str
    name: str


class TagAdminListPublic(SQLModel):
    data: list[TagAdminPublic]
