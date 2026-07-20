from sqlmodel import SQLModel


class GenreCreate(SQLModel):
    genre_name: str
    genre_sid: str


class GenreUpdate(SQLModel):
    genre_name: str | None = None
    genre_sid: str | None = None


class GenreAdminPublic(SQLModel):
    genre_id: int
    genre_name: str
    genre_sid: str


class GenreAdminListPublic(SQLModel):
    data: list[GenreAdminPublic]
