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


class AnimeUpdate(SQLModel):
    # `type` is deliberately not editable here - switching movie/tv would
    # mean restructuring Content.content_type and adding/removing the
    # Post-vs-seasons split, not a plain field edit.
    anime_name: str | None = None
    overview: str | None = None
    duration: int | None = None
    rating: decimal.Decimal | None = None
    age_id: int | None = None
    poster_source: NewImageSource | None = None
    poster_img: str | None = None
    backdrop_source: NewImageSource | None = None
    backdrop_img: str | None = None
    anime_tmdb_id: int | None = None
    anime_rel_date: dt.date | None = None
    genre_ids: list[int] | None = None


class AnimeAdminPublic(SQLModel):
    anime_id: int
    slug: str
    anime_name: str
    type: str
    # What POST /admin/content/{content_id}/links expects - only present
    # for type="movie". None for type="tv": that anime still has its own
    # Content row internally (content_id is NOT NULL), but downloads for a
    # tv show live on its episodes'/packs' own content_id instead, and that
    # row is never a valid link/comment/view-tracking target (see
    # ContentContentType.TV) - not exposing it here avoids the field being
    # mistaken for something attachable.
    content_id: int | None
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
