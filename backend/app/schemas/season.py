import datetime as dt
import decimal

from sqlmodel import SQLModel

from app.schemas.common import ImageUrls
from app.schemas.episode import EpisodeSummary
from app.schemas.pack import PackSummary


class SeasonSummary(SQLModel):
    season_number: int
    season_name: str
    poster: ImageUrls
    rating: decimal.Decimal
    episode_count: int
    pack_count: int


class SeasonDetail(SQLModel):
    season_number: int
    season_name: str
    poster: ImageUrls
    overview: str
    rating: decimal.Decimal
    release_date: dt.date | None
    episodes: list[EpisodeSummary]
    packs: list[PackSummary]
