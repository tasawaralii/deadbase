import datetime as dt
import decimal

from sqlmodel import SQLModel

from app.schemas.common import DownloadLink, ImageUrls, LinkPublic
from app.schemas.season import SeasonSummary


class AnimeSummary(SQLModel):
    slug: str
    anime_name: str
    type: str
    poster: ImageUrls
    rating: decimal.Decimal
    age_rating: str
    genres: list[str]
    season_count: int | None


class AnimeDetail(SQLModel):
    content_id: int
    slug: str
    anime_name: str
    type: str
    poster: ImageUrls
    backdrop: ImageUrls
    overview: str
    duration: int
    rating: decimal.Decimal
    age_rating: str
    genres: list[str]
    release_date: dt.date | None
    seasons: list[SeasonSummary] | None = None
    links: list[LinkPublic] | None = None
    watch_servers: list[DownloadLink] | None = None


class AnimeListPublic(SQLModel):
    data: list[AnimeSummary]
    page: int
    limit: int
    count: int
