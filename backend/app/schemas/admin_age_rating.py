from sqlmodel import SQLModel


class AgeRatingCreate(SQLModel):
    age_name: str
    age_des: str


class AgeRatingUpdate(SQLModel):
    age_name: str | None = None
    age_des: str | None = None


class AgeRatingAdminPublic(SQLModel):
    age_id: int
    age_name: str
    age_des: str


class AgeRatingAdminListPublic(SQLModel):
    data: list[AgeRatingAdminPublic]
