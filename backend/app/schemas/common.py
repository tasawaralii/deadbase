from sqlmodel import SQLModel


class ImageUrls(SQLModel):
    low: str
    mid: str
    high: str


class DownloadLink(SQLModel):
    name: str
    link: str
    color: str


class LinkPublic(SQLModel):
    quality: str
    size: str
    servers: list[DownloadLink]
    only_hindi: bool
    note: str


class SeasonDub(SQLModel):
    platform: str
    language: str
