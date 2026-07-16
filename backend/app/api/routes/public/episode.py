from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.api.deps import SessionDep
from app.media import build_download_links, get_watch_servers, resolve_image_urls
from app.models import Animes, Episodes, Seasons
from app.schemas.episode import EpisodeDetail

router = APIRouter()


@router.get("/anime/{slug}/season/{season_number}/episode/{episode_number}")
def read_episode(
    session: SessionDep, slug: str, season_number: int, episode_number: int
) -> EpisodeDetail:
    anime = session.exec(select(Animes).where(Animes.slug == slug)).first()
    if not anime:
        raise HTTPException(status_code=404, detail="Anime not found")

    season = session.exec(
        select(Seasons).where(
            Seasons.anime_id == anime.anime_id,
            Seasons.season_number == season_number,
        )
    ).first()
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")

    episode = session.exec(
        select(Episodes).where(
            Episodes.season_id == season.season_id,
            Episodes.episode_number == episode_number,
        )
    ).first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")

    return EpisodeDetail(
        episode_number=episode.episode_number,
        episode_name=episode.episode_name,
        overview=episode.overview,
        img=resolve_image_urls("tmdb", episode.img, "backdrop"),
        air_date=episode.air_date,
        episode_runtime=episode.episode_runtime,
        episode_rating=episode.episode_rating,
        links=build_download_links(session, episode.content_id),
        watch_servers=get_watch_servers(),
    )
