from sqlmodel import SQLModel


class SeasonDubCreate(SQLModel):
    ott_id: int
    language_id: int


class SeasonDubAdminPublic(SQLModel):
    season_id: int
    ott_id: int
    ott_name: str
    language_id: int
    language_name: str


class SeasonDubListPublic(SQLModel):
    data: list[SeasonDubAdminPublic]
