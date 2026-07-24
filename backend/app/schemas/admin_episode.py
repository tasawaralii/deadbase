import datetime as dt
import decimal

from sqlmodel import SQLModel

from app.schemas.common import ImageUrls


class EpisodeCreateItem(SQLModel):
    # Author-assigned, local to this season - decoupled from whatever
    # numbering the source (e.g. a mis-numbered tmdb episode group) used.
    episode_number: int
    episode_name: str | None = None
    overview: str | None = None
    # Raw tmdb-relative path - Episodes has no source column of its own,
    # the public API always resolves this as a tmdb path (see
    # app.api.routes.public.episode). A bucket-uploaded still isn't
    # representable here yet.
    img: str | None = None
    air_date: dt.date | None = None
    episode_runtime: int | None = None
    episode_rating: decimal.Decimal | None = None
    episode_tmdb_id: str | None = None
    note: str | None = None


class EpisodeBatchCreate(SQLModel):
    episodes: list[EpisodeCreateItem]


class EpisodeUpdate(SQLModel):
    episode_number: int | None = None
    episode_name: str | None = None
    overview: str | None = None
    img: str | None = None
    air_date: dt.date | None = None
    episode_runtime: int | None = None
    episode_rating: decimal.Decimal | None = None
    episode_tmdb_id: str | None = None
    note: str | None = None


class EpisodeAdminPublic(SQLModel):
    episode_id: int
    season_id: int
    # What POST /admin/content/{content_id}/links expects.
    content_id: int
    episode_number: int
    episode_name: str | None
    overview: str | None
    img: ImageUrls
    air_date: dt.date | None
    episode_runtime: int | None
    episode_rating: decimal.Decimal | None
    episode_tmdb_id: str | None
    note: str | None
    link_count: int


class EpisodeBatchPublic(SQLModel):
    data: list[EpisodeAdminPublic]
