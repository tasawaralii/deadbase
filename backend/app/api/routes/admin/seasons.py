import decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from app.api.deps import CurrentAuthor, SessionDep, get_current_author
from app.media import resolve_image_urls
from app.models import Animes, Seasons
from app.permissions import require_anime_write_access
from app.posts import create_post_for_season
from app.schemas.admin_season import SeasonAdminPublic, SeasonCreate

router = APIRouter(
    prefix="/animes/{anime_id}/seasons",
    tags=["admin"],
    dependencies=[Depends(get_current_author)],
)


@router.post("/")
def create_season(
    session: SessionDep, author: CurrentAuthor, anime_id: int, body: SeasonCreate
) -> SeasonAdminPublic:
    anime = session.get(Animes, anime_id)
    if anime is None:
        raise HTTPException(status_code=404, detail="Anime not found")

    if anime.type != "tv":
        raise HTTPException(
            status_code=400, detail="Only TV-type anime can have seasons added"
        )

    require_anime_write_access(session, author, anime_id)

    existing = session.exec(
        select(Seasons).where(
            Seasons.anime_id == anime_id, Seasons.season_number == body.season_number
        )
    ).first()
    if existing is not None:
        raise HTTPException(
            status_code=400,
            detail=f"Season {body.season_number} already exists for this anime",
        )

    season = Seasons(
        anime_id=anime_id,
        season_number=body.season_number,
        season_name=body.season_name,
        total_episodes=body.total_episodes,
        season_overview=body.season_overview,
        poster_source=body.poster_source,
        poster_img=body.poster_img,
        rating=body.rating if body.rating is not None else decimal.Decimal("0.00"),
        season_tmdb_id=body.season_tmdb_id,
        season_rel_date=body.season_rel_date,
    )
    session.add(season)
    session.flush()

    post = create_post_for_season(session, anime, season, author)

    session.commit()
    session.refresh(season)

    return SeasonAdminPublic(
        season_id=season.season_id,
        anime_id=anime_id,
        season_number=season.season_number,
        season_name=season.season_name,
        total_episodes=season.total_episodes,
        season_overview=season.season_overview,
        poster=resolve_image_urls(season.poster_source, season.poster_img, "poster"),
        rating=season.rating,
        season_tmdb_id=season.season_tmdb_id,
        season_rel_date=season.season_rel_date,
        post_slug=post.slug,
    )
