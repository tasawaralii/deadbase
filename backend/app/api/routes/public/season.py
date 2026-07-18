from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import Session, col, func, select

from app.api.deps import SessionDep
from app.media import resolve_image_urls
from app.models import Animes, Episodes, Links, Packs, SeasonDubs, Seasons
from app.schemas.common import SeasonDub
from app.schemas.episode import EpisodeSummary
from app.schemas.pack import PackSummary
from app.schemas.season import SeasonDetail

router = APIRouter()


def build_season_detail(session: Session, season: Seasons) -> SeasonDetail:
    episode_link_count_subq = (
        select(func.count(col(Links.link_id)))
        .where(Links.content_id == Episodes.content_id, Links.is_live == True)  # noqa: E712
        .scalar_subquery()
    )
    episodes = session.exec(
        select(Episodes, episode_link_count_subq)
        .where(Episodes.season_id == season.season_id, episode_link_count_subq > 0)
        .order_by(col(Episodes.episode_number).asc())
    ).all()

    pack_link_count_subq = (
        select(func.count(col(Links.link_id)))
        .where(Links.content_id == Packs.content_id, Links.is_live == True)  # noqa: E712
        .scalar_subquery()
    )
    packs = session.exec(
        select(Packs, pack_link_count_subq)
        .where(Packs.season_id == season.season_id, pack_link_count_subq > 0)
        .order_by(col(Packs.start_ep).asc())
    ).all()

    dubs = session.exec(
        select(SeasonDubs)
        .where(SeasonDubs.season_id == season.season_id)
        .options(
            selectinload(SeasonDubs.ott),  # type: ignore[arg-type]
            selectinload(SeasonDubs.language),  # type: ignore[arg-type]
        )
    ).all()

    return SeasonDetail(
        season_number=season.season_number,
        season_name=season.season_name,
        poster=resolve_image_urls(season.poster_source, season.poster_img, "poster"),
        overview=season.season_overview or season.anime.overview,
        rating=season.rating,
        release_date=season.season_rel_date,
        total_episodes=season.total_episodes,
        dubs=[
            SeasonDub(platform=dub.ott.ott_name, language=dub.language.language_name)
            for dub in dubs
        ],
        episodes=[
            EpisodeSummary(
                episode_number=episode.episode_number,
                episode_name=episode.episode_name,
                note=episode.note,
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

    return build_season_detail(session, season)
