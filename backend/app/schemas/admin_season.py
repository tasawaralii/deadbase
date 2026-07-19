import datetime as dt
import decimal

from sqlmodel import SQLModel

from app.schemas.common import ImageUrls, NewImageSource


class SeasonCreate(SQLModel):
    season_number: int
    season_name: str
    total_episodes: int
    season_overview: str
    poster_source: NewImageSource
    poster_img: str
    rating: decimal.Decimal | None = None
    season_tmdb_id: str | None = None
    season_rel_date: dt.date | None = None


class SeasonAdminPublic(SQLModel):
    season_id: int
    anime_id: int
    season_number: int
    season_name: str
    total_episodes: int
    season_overview: str
    poster: ImageUrls
    rating: decimal.Decimal
    season_tmdb_id: str | None
    season_rel_date: dt.date | None
    post_slug: str


class SeasonAdminSummary(SQLModel):
    season_id: int
    season_number: int
    season_name: str
    poster: ImageUrls
    # episode_count: episodes actually added so far. total_episodes: what
    # the season is expected to have (from TMDB or the author's own count).
    episode_count: int
    total_episodes: int
    post_slug: str | None
