import datetime as dt
import decimal
from typing import Literal

from sqlmodel import SQLModel

from app.schemas.common import ImageUrls

# New content only ever gets created with a tmdb-sourced or freshly-uploaded
# bucket image - "url" and legacy "local" are read-only holdovers from the
# old PHP migration, never offered for new rows.
NewImageSource = Literal["tmdb", "bucket"]


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
