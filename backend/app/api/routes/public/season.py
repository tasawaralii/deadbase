from fastapi import APIRouter, HTTPException
from sqlmodel import col, func, select

from app.api.deps import SessionDep
from app.media import resolve_image_urls
from app.models import Animes, Episodes, Links, Packs, Seasons
from app.schemas.episode import EpisodeSummary
from app.schemas.pack import PackSummary
from app.schemas.season import SeasonDetail

router = APIRouter()


@router.get("/anime/{slug}/season/{season_number}")
def read_season(session: SessionDep, slug: str, season_number: int) -> SeasonDetail:
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

    episode_link_count_subq = (
        select(func.count(col(Links.link_id)))
        .where(Links.content_id == Episodes.content_id, Links.is_live == True)  # noqa: E712
        .scalar_subquery()
    )
    episodes = session.exec(
        select(Episodes, episode_link_count_subq)
        .where(Episodes.season_id == season.season_id)
        .order_by(col(Episodes.episode_number).asc())
    ).all()

    pack_link_count_subq = (
        select(func.count(col(Links.link_id)))
        .where(Links.content_id == Packs.content_id, Links.is_live == True)  # noqa: E712
        .scalar_subquery()
    )
    packs = session.exec(
        select(Packs, pack_link_count_subq)
        .where(Packs.season_id == season.season_id)
        .order_by(col(Packs.start_ep).asc())
    ).all()

    return SeasonDetail(
        season_number=season.season_number,
        season_name=season.season_name,
        poster=resolve_image_urls(season.poster_source, season.poster_img, "poster"),
        overview=season.season_overview,
        rating=season.rating,
        release_date=season.season_rel_date,
        episodes=[
            EpisodeSummary(
                episode_number=episode.episode_number,
                episode_name=episode.episode_name,
                img=resolve_image_urls("tmdb", episode.img, "backdrop"),
                air_date=episode.air_date,
                episode_rating=episode.episode_rating,
                link_count=link_count,
            )
            for episode, link_count in episodes
        ],
        packs=[
            PackSummary(
                pack_name=pack.pack_name,
                start_ep=pack.start_ep,
                end_ep=pack.end_ep,
                link_count=link_count,
            )
            for pack, link_count in packs
        ],
    )
