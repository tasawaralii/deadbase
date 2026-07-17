from fastapi import APIRouter, HTTPException, Query
from sqlmodel import col, func, select

from app.api.deps import SessionDep, VisitorId
from app.media import resolve_image_urls
from app.models import Episodes, Links, Message, Packs, Seasons
from app.schemas.anime import AnimeSummary
from app.schemas.episode import EpisodeSummary
from app.schemas.season import SeasonSummary
from app.schemas.trending import (
    TrendingAnimeItem,
    TrendingAnimeList,
    TrendingEpisodeItem,
    TrendingEpisodeList,
    TrendingSeasonItem,
    TrendingSeasonList,
)
from app.trending import (
    TrendingWindow,
    get_trending_anime,
    get_trending_episodes,
    get_trending_seasons,
    record_view,
)

router = APIRouter()


@router.post("/track/view/{content_id}")
def track_view(session: SessionDep, visitor_id: VisitorId, content_id: int) -> Message:
    try:
        record_view(session, visitor_id, content_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return Message(message="Recorded")


@router.get("/trending/anime")
def trending_anime(
    session: SessionDep,
    window: TrendingWindow = Query("today"),
    limit: int = Query(20, ge=1, le=50),
) -> TrendingAnimeList:
    rows = get_trending_anime(session, window, limit)

    data = []
    for anime, views in rows:
        season_count = None
        if anime.type != "movie":
            season_count = session.exec(
                select(func.count(col(Seasons.season_id))).where(
                    Seasons.anime_id == anime.anime_id
                )
            ).one()
        data.append(
            TrendingAnimeItem(
                anime=AnimeSummary(
                    slug=anime.slug,
                    anime_name=anime.anime_name,
                    type=anime.type,
                    poster=resolve_image_urls(
                        anime.poster_source, anime.poster_img, "poster"
                    ),
                    rating=anime.rating,
                    age_rating=anime.age.age_name,
                    genres=[g.genre_name for g in anime.genre],
                    season_count=season_count,
                ),
                views=views,
            )
        )
    return TrendingAnimeList(data=data)


@router.get("/trending/seasons")
def trending_seasons(
    session: SessionDep,
    window: TrendingWindow = Query("today"),
    limit: int = Query(20, ge=1, le=50),
) -> TrendingSeasonList:
    rows = get_trending_seasons(session, window, limit)

    data = []
    for season, views in rows:
        episode_count = session.exec(
            select(func.count(col(Episodes.episode_id))).where(
                Episodes.season_id == season.season_id
            )
        ).one()
        pack_count = session.exec(
            select(func.count(col(Packs.pack_id))).where(
                Packs.season_id == season.season_id
            )
        ).one()
        data.append(
            TrendingSeasonItem(
                anime_slug=season.anime.slug,
                season=SeasonSummary(
                    season_number=season.season_number,
                    season_name=season.season_name,
                    poster=resolve_image_urls(
                        season.poster_source, season.poster_img, "poster"
                    ),
                    rating=season.rating,
                    episode_count=episode_count,
                    pack_count=pack_count,
                ),
                views=views,
            )
        )
    return TrendingSeasonList(data=data)


@router.get("/trending/episodes")
def trending_episodes(
    session: SessionDep,
    window: TrendingWindow = Query("today"),
    limit: int = Query(20, ge=1, le=50),
) -> TrendingEpisodeList:
    rows = get_trending_episodes(session, window, limit)

    data = []
    for episode, views in rows:
        link_count = session.exec(
            select(func.count(col(Links.link_id))).where(
                Links.content_id == episode.content_id,
                Links.is_live == True,  # noqa: E712
            )
        ).one()
        data.append(
            TrendingEpisodeItem(
                anime_slug=episode.season.anime.slug,
                season_number=episode.season.season_number,
                episode=EpisodeSummary(
                    episode_number=episode.episode_number,
                    episode_name=episode.episode_name,
                    img=resolve_image_urls("tmdb", episode.img, "backdrop"),
                    air_date=episode.air_date,
                    episode_rating=episode.episode_rating,
                    link_count=link_count,
                ),
                views=views,
            )
        )
    return TrendingEpisodeList(data=data)
