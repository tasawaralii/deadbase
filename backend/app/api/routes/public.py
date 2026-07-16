from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.api.deps import SessionDep
from app.models import (
    Animes,
    EpisodeDetailPublic,
    EpisodePublic,
    Episodes,
    LinkPublic,
    Links,
    LinkServerPublic,
    LinkServers,
    QualityPublic,
    SeasonPosterPublic,
    Seasons,
    ServerPublic,
)

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/anime/{slug}/{season_number}/{episode_number}")
def read_episode(
    session: SessionDep, slug: str, season_number: int, episode_number: int
) -> EpisodeDetailPublic:
    """
    Get an episode's season poster, details, and download links/servers.
    """
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

    links = session.exec(
        select(Links)
        .where(Links.content_id == episode.content_id, Links.is_live == True)  # noqa: E712
        .options(
            selectinload(Links.quality),  # type: ignore[arg-type]
            selectinload(Links.link_servers).selectinload(  # type: ignore[arg-type]
                LinkServers.server  # type: ignore[arg-type]
            ),
        )
    ).all()

    return EpisodeDetailPublic(
        season_poster=SeasonPosterPublic(
            source=season.poster_source, image=season.poster_img
        ),
        episode=EpisodePublic.model_validate(episode),
        links=[
            LinkPublic(
                filename=link.filename,
                type=link.type,
                size=link.size,
                duration=link.duration,
                quality=QualityPublic.model_validate(link.quality)
                if link.quality
                else None,
                servers=[
                    LinkServerPublic(
                        slug=ls.slug,
                        server=ServerPublic.model_validate(ls.server),
                    )
                    for ls in link.link_servers
                    if ls.server.is_enabled
                ],
            )
            for link in links
        ],
    )
