from sqlmodel import SQLModel

from app.schemas.anime import AnimeSummary
from app.schemas.episode import EpisodeSummary
from app.schemas.season import SeasonSummary


class TrendingAnimeItem(SQLModel):
    anime: AnimeSummary
    views: int


class TrendingSeasonItem(SQLModel):
    anime_slug: str
    anime_name: str
    season: SeasonSummary
    views: int


class TrendingEpisodeItem(SQLModel):
    anime_slug: str
    anime_name: str
    season_number: int
    episode: EpisodeSummary
    views: int


class TrendingAnimeList(SQLModel):
    data: list[TrendingAnimeItem]


class TrendingSeasonList(SQLModel):
    data: list[TrendingSeasonItem]


class TrendingEpisodeList(SQLModel):
    data: list[TrendingEpisodeItem]
