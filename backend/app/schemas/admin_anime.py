import datetime as dt
import decimal
from typing import Literal

from sqlmodel import SQLModel

from app.schemas.admin_season import SeasonAdminSummary
from app.schemas.common import ImageUrls, NewImageSource


class AnimeCreate(SQLModel):
    anime_name: str
    type: Literal["movie", "tv"]
    overview: str
    duration: int
    rating: decimal.Decimal
    age_id: int
    poster_source: NewImageSource
    poster_img: str
    backdrop_source: NewImageSource
    backdrop_img: str
    anime_tmdb_id: int | None = None
    anime_rel_date: dt.date | None = None
    genre_ids: list[int] = []


class AnimeAdminPublic(SQLModel):
    anime_id: int
    slug: str
    anime_name: str
    type: str
    # For type="movie" this is what POST /admin/content/{content_id}/links
    # expects. TV shows have one too (every anime gets a Content row) but
    # downloads for a TV show live on its episodes/packs instead - this
    # isn't the one authors attach links to for type="tv".
    content_id: int
    poster: ImageUrls
    backdrop: ImageUrls
    overview: str
    duration: int
    rating: decimal.Decimal
    age_id: int
    anime_tmdb_id: int | None
    anime_rel_date: dt.date | None
    genres: list[str]
    # Set only for type="movie" - a movie's Post is created in the same
    # request. TV shows get a Post per season instead, created when a season
    # is added, not here.
    post_slug: str | None


class AnimeAdminDetail(AnimeAdminPublic):
    seasons: list[SeasonAdminSummary]


class AnimeAdminSummary(SQLModel):
    anime_id: int
    slug: str
    anime_name: str
    type: str
    poster: ImageUrls
    rating: decimal.Decimal
    season_count: int


class AnimeAdminListPublic(SQLModel):
    data: list[AnimeAdminSummary]
    count: int
