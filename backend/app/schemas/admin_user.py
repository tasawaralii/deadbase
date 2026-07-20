from sqlmodel import SQLModel


class AnimeAccessGrantPublic(SQLModel):
    anime_id: int
    slug: str
    anime_name: str
    type: str


class AnimeAccessListPublic(SQLModel):
    data: list[AnimeAccessGrantPublic]
