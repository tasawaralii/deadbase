from sqlmodel import SQLModel

from app.schemas.common import ImageUrls


class TmdbSearchResult(SQLModel):
    tmdb_id: int
    title: str
    overview: str
    poster: ImageUrls
    backdrop: ImageUrls
    # Raw tmdb-relative paths - what actually gets stored in
    # Animes.poster_img/backdrop_img (with *_source="tmdb") if this result
    # is picked without a further detail fetch.
    poster_path: str | None
    backdrop_path: str | None
    release_date: str | None
    rating: float


class TmdbSearchResults(SQLModel):
    results: list[TmdbSearchResult]


class TmdbSeasonSummary(SQLModel):
    id: str
    season_number: int
    name: str
    episode_count: int
    air_date: str | None
    poster: ImageUrls
    # Raw tmdb-relative path (e.g. "/xyz.jpg") - this, not the resolved
    # `poster` above, is what actually gets stored in Seasons.poster_img
    # (with poster_source="tmdb") when this season is imported.
    poster_path: str | None


class TmdbShowDetail(SQLModel):
    tmdb_id: int
    title: str
    overview: str
    poster: ImageUrls
    backdrop: ImageUrls
    # Raw tmdb-relative paths - what actually gets stored in
    # Animes.poster_img/backdrop_img (with *_source="tmdb"), since those
    # columns hold a path resolve_image_urls() re-expands later, not a URL.
    poster_path: str | None
    backdrop_path: str | None
    first_air_date: str | None
    rating: float
    genres: list[str]
    seasons: list[TmdbSeasonSummary]


class TmdbMovieDetail(SQLModel):
    tmdb_id: int
    title: str
    overview: str
    poster: ImageUrls
    backdrop: ImageUrls
    poster_path: str | None
    backdrop_path: str | None
    release_date: str | None
    rating: float
    runtime: int | None
    genres: list[str]


class TmdbEpisodeSummary(SQLModel):
    id: str
    episode_number: int
    name: str
    overview: str
    air_date: str | None
    runtime: int | None
    rating: float
    still: ImageUrls
    # Raw tmdb-relative path - what actually gets stored in Episodes.img.
    still_path: str | None


class TmdbSeasonDetail(SQLModel):
    id: str
    season_number: int
    name: str
    overview: str
    poster: ImageUrls
    poster_path: str | None
    air_date: str | None
    episodes: list[TmdbEpisodeSummary]


class TmdbEpisodeGroupSummary(SQLModel):
    id: str
    name: str
    group_count: int
    episode_count: int


class TmdbEpisodeGroupList(SQLModel):
    groups: list[TmdbEpisodeGroupSummary]


class TmdbEpisodeGroupItem(SQLModel):
    id: str
    name: str
    order: int
    # Numbered as TMDB stores them in this group - often globally sequential
    # across a mixed season rather than reset per-season, see
    # app.api.routes.admin.tmdb for how authors are expected to handle this.
    episodes: list[TmdbEpisodeSummary]


class TmdbEpisodeGroupDetail(SQLModel):
    id: str
    name: str
    groups: list[TmdbEpisodeGroupItem]
