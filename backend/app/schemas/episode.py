import datetime as dt
import decimal

from sqlmodel import SQLModel

from app.schemas.common import DownloadLink, ImageUrls, LinkPublic


class EpisodeSummary(SQLModel):
    episode_number: int
    episode_name: str | None
    img: ImageUrls
    air_date: dt.date | None
    episode_rating: decimal.Decimal | None
    link_count: int


class EpisodeDetail(SQLModel):
    content_id: int
    episode_number: int
    episode_name: str | None
    overview: str | None
    img: ImageUrls
    air_date: dt.date | None
    episode_runtime: int | None
    episode_rating: decimal.Decimal | None
    links: list[LinkPublic]
    watch_servers: list[DownloadLink]
