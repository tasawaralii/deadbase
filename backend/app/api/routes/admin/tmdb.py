from typing import Literal

from fastapi import APIRouter, Depends, Query

from app import tmdb
from app.api.deps import get_current_author
from app.schemas.tmdb import (
    TmdbEpisodeGroupDetail,
    TmdbEpisodeGroupList,
    TmdbEpisodeSummary,
    TmdbMovieDetail,
    TmdbSearchResults,
    TmdbSeasonDetail,
    TmdbShowDetail,
)

router = APIRouter(
    prefix="/tmdb", tags=["admin"], dependencies=[Depends(get_current_author)]
)


@router.get("/search")
def search_tmdb(
    query: str, media_type: Literal["tv", "movie"] = Query("tv", alias="type")
) -> TmdbSearchResults:
    return tmdb.search(query, media_type)


@router.get("/tv/{tmdb_id}")
def get_tv_show(tmdb_id: int) -> TmdbShowDetail:
    return tmdb.get_tv(tmdb_id)


@router.get("/movie/{tmdb_id}")
def get_movie(tmdb_id: int) -> TmdbMovieDetail:
    return tmdb.get_movie(tmdb_id)


@router.get("/season/{season_tmdb_id}")
def get_tv_season(season_tmdb_id: str) -> TmdbSeasonDetail:
    """
    season_tmdb_id is "{tmdb_id}-s{season_number}" - the exact string stored
    in Seasons.season_tmdb_id, so a later resync is a pure passthrough with
    no anime_id lookup or reconstruction needed.
    """
    tmdb_id, season_number = tmdb.parse_season_id(season_tmdb_id)
    return tmdb.get_season(tmdb_id, season_number)


@router.get("/episode/{episode_tmdb_id}")
def get_tv_episode(episode_tmdb_id: str) -> TmdbEpisodeSummary:
    """
    episode_tmdb_id is "{tmdb_id}-s{season_number}-e{episode_number}" - the
    exact string stored in Episodes.episode_tmdb_id, same passthrough
    rationale as get_tv_season above.
    """
    tmdb_id, season_number, episode_number = tmdb.parse_episode_id(episode_tmdb_id)
    return tmdb.get_episode(tmdb_id, season_number, episode_number)


@router.get("/tv/{tmdb_id}/episode_groups")
def get_tv_episode_groups(tmdb_id: int) -> TmdbEpisodeGroupList:
    return tmdb.get_episode_groups(tmdb_id)


@router.get("/episode_group/{group_id}")
def get_episode_group(group_id: str) -> TmdbEpisodeGroupDetail:
    return tmdb.get_episode_group(group_id)
