from fastapi import APIRouter, HTTPException, Path
from sqlmodel import select

from app.api.deps import SessionDep
from app.media import build_download_links, get_watch_servers
from app.models import Animes, Packs, Seasons
from app.schemas.pack import PackDetail

router = APIRouter()


@router.get("/anime/{slug}/season/{season_number}/pack/{episode_range}")
def read_pack(
    session: SessionDep,
    slug: str,
    season_number: int,
    episode_range: str = Path(pattern=r"^\d+-\d+$"),
) -> PackDetail:
    start_ep_str, end_ep_str = episode_range.split("-", 1)
    start_ep, end_ep = int(start_ep_str), int(end_ep_str)

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

    pack = session.exec(
        select(Packs).where(
            Packs.season_id == season.season_id,
            Packs.start_ep == start_ep,
            Packs.end_ep == end_ep,
        )
    ).first()
    if not pack:
        raise HTTPException(status_code=404, detail="Pack not found")

    return PackDetail(
        pack_name=pack.pack_name,
        start_ep=pack.start_ep,
        end_ep=pack.end_ep,
        links=build_download_links(session, pack.content_id),
        watch_servers=get_watch_servers(),
    )
