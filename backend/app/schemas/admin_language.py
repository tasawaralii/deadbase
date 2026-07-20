from sqlmodel import SQLModel


class LanguageCreate(SQLModel):
    language_sid: str
    language_name: str


class LanguageUpdate(SQLModel):
    language_sid: str | None = None
    language_name: str | None = None


class LanguageAdminPublic(SQLModel):
    language_id: int
    language_sid: str
    language_name: str


class LanguageAdminListPublic(SQLModel):
    data: list[LanguageAdminPublic]
