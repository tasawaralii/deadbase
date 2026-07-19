from typing import Any, Literal

import httpx
from fastapi import HTTPException

from app.core.config import settings
from app.media import resolve_image_urls
from app.schemas.tmdb import (
    TmdbEpisodeGroupDetail,
    TmdbEpisodeGroupItem,
    TmdbEpisodeGroupList,
    TmdbEpisodeGroupSummary,
    TmdbEpisodeSummary,
    TmdbMovieDetail,
    TmdbSearchResult,
    TmdbSearchResults,
    TmdbSeasonDetail,
    TmdbSeasonSummary,
    TmdbShowDetail,
)

_BASE_URL = "https://api.themoviedb.org/3"


def _get(path: str, params: dict[str, str] | None = None) -> dict[str, Any]:
    if not settings.TMDB_API_KEY:
        raise HTTPException(status_code=503, detail="TMDB API key is not configured")

    query = {"api_key": settings.TMDB_API_KEY, **(params or {})}
    response = httpx.get(f"{_BASE_URL}{path}", params=query, timeout=10)
    if response.status_code >= 400:
        detail = "TMDB request failed"
        try:
            detail = response.json().get("status_message", detail)
        except ValueError:
            pass
        raise HTTPException(status_code=response.status_code, detail=detail)
    result: dict[str, Any] = response.json()
    return result


def search(query: str, media_type: Literal["tv", "movie"]) -> TmdbSearchResults:
    data = _get(f"/search/{media_type}", {"query": query})
    results = [
        TmdbSearchResult(
            tmdb_id=r["id"],
            title=r.get("name") or r.get("title") or "",
            overview=r.get("overview", ""),
            poster=resolve_image_urls("tmdb", r.get("poster_path"), "poster"),
            backdrop=resolve_image_urls("tmdb", r.get("backdrop_path"), "backdrop"),
            poster_path=r.get("poster_path"),
            backdrop_path=r.get("backdrop_path"),
            release_date=r.get("first_air_date") or r.get("release_date") or None,
            rating=r.get("vote_average", 0.0),
        )
        for r in data.get("results", [])
    ]
    return TmdbSearchResults(results=results)


def get_tv(tmdb_id: int) -> TmdbShowDetail:
    data = _get(f"/tv/{tmdb_id}")
    seasons = [
        TmdbSeasonSummary(
            id=f"{tmdb_id}-s{s['season_number']}",
            season_number=s["season_number"],
            name=s.get("name", ""),
            episode_count=s.get("episode_count", 0),
            air_date=s.get("air_date"),
            poster=resolve_image_urls("tmdb", s.get("poster_path"), "poster"),
            poster_path=s.get("poster_path"),
        )
        for s in data.get("seasons", [])
    ]
    return TmdbShowDetail(
        tmdb_id=data["id"],
        title=data.get("name", ""),
        overview=data.get("overview", ""),
        poster=resolve_image_urls("tmdb", data.get("poster_path"), "poster"),
        backdrop=resolve_image_urls("tmdb", data.get("backdrop_path"), "backdrop"),
        poster_path=data.get("poster_path"),
        backdrop_path=data.get("backdrop_path"),
        first_air_date=data.get("first_air_date"),
        rating=data.get("vote_average", 0.0),
        genres=[g["name"] for g in data.get("genres", [])],
        seasons=seasons,
    )


def get_movie(tmdb_id: int) -> TmdbMovieDetail:
    data = _get(f"/movie/{tmdb_id}")
    return TmdbMovieDetail(
        tmdb_id=data["id"],
        title=data.get("title", ""),
        overview=data.get("overview", ""),
        poster=resolve_image_urls("tmdb", data.get("poster_path"), "poster"),
        backdrop=resolve_image_urls("tmdb", data.get("backdrop_path"), "backdrop"),
        poster_path=data.get("poster_path"),
        backdrop_path=data.get("backdrop_path"),
        release_date=data.get("release_date"),
        rating=data.get("vote_average", 0.0),
        runtime=data.get("runtime"),
        genres=[g["name"] for g in data.get("genres", [])],
    )


def _episode_summary(e: dict[str, Any]) -> TmdbEpisodeSummary:
    # show_id/season_number/episode_number here are the episode's own native
    # identity in TMDB - present on every episode object regardless of
    # whether it came from a plain season fetch or an episode group, so this
    # id is stable even when browsing a group that relabels/reorders it.
    return TmdbEpisodeSummary(
        id=f"{e['show_id']}-s{e['season_number']}-e{e['episode_number']}",
        episode_number=e["episode_number"],
        name=e.get("name", ""),
        overview=e.get("overview", ""),
        air_date=e.get("air_date"),
        runtime=e.get("runtime"),
        rating=e.get("vote_average", 0.0),
        still=resolve_image_urls("tmdb", e.get("still_path"), "backdrop"),
        still_path=e.get("still_path"),
    )


def get_season(tmdb_id: int, season_number: int) -> TmdbSeasonDetail:
    data = _get(f"/tv/{tmdb_id}/season/{season_number}")
    return TmdbSeasonDetail(
        id=f"{tmdb_id}-s{season_number}",
        season_number=data["season_number"],
        name=data.get("name", ""),
        overview=data.get("overview", ""),
        poster=resolve_image_urls("tmdb", data.get("poster_path"), "poster"),
        poster_path=data.get("poster_path"),
        air_date=data.get("air_date"),
        episodes=[_episode_summary(e) for e in data.get("episodes", [])],
    )


def get_episode(tmdb_id: int, season_number: int, episode_number: int) -> TmdbEpisodeSummary:
    data = _get(f"/tv/{tmdb_id}/season/{season_number}/episode/{episode_number}")
    data.setdefault("show_id", tmdb_id)
    return _episode_summary(data)


def parse_season_id(season_tmdb_id: str) -> tuple[int, int]:
    """Splits "{tmdb_id}-s{season_number}" back into its parts."""
    try:
        tmdb_id_str, season_str = season_tmdb_id.split("-s")
        return int(tmdb_id_str), int(season_str)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="Malformed season id, expected '{tmdb_id}-s{season_number}'",
        ) from exc


def parse_episode_id(episode_tmdb_id: str) -> tuple[int, int, int]:
    """Splits "{tmdb_id}-s{season_number}-e{episode_number}" back into its parts."""
    try:
        tmdb_id_str, rest = episode_tmdb_id.split("-s")
        season_str, episode_str = rest.split("-e")
        return int(tmdb_id_str), int(season_str), int(episode_str)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=(
                "Malformed episode id, expected "
                "'{tmdb_id}-s{season_number}-e{episode_number}'"
            ),
        ) from exc


def get_episode_groups(tmdb_id: int) -> TmdbEpisodeGroupList:
    """
    Some anime have all episodes across multiple real seasons flattened into
    a single TMDB "season" - episode groups are TMDB's own workaround, an
    alternate season split some (not all) shows also have populated. Authors
    fall back to browsing these manually when the default season data looks
    wrong (see app.api.routes.admin.tmdb.get_episode_group).
    """
    data = _get(f"/tv/{tmdb_id}/episode_groups")
    groups = [
        TmdbEpisodeGroupSummary(
            id=g["id"],
            name=g.get("name", ""),
            group_count=g.get("group_count", 0),
            episode_count=g.get("episode_count", 0),
        )
        for g in data.get("results", [])
    ]
    return TmdbEpisodeGroupList(groups=groups)


def get_episode_group(group_id: str) -> TmdbEpisodeGroupDetail:
    data = _get(f"/tv/episode_group/{group_id}")
    groups = [
        TmdbEpisodeGroupItem(
            id=g["id"],
            name=g.get("name", ""),
            order=g.get("order", 0),
            episodes=[_episode_summary(e) for e in g.get("episodes", [])],
        )
        for g in data.get("groups", [])
    ]
    return TmdbEpisodeGroupDetail(
        id=data["id"], name=data.get("name", ""), groups=groups
    )
