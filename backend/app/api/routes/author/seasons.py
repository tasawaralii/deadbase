import decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from app.api.deps import CurrentAuthor, SessionDep, get_current_author
from app.media import resolve_image_urls
from app.models import Animes, Posts, Seasons
from app.permissions import require_anime_write_access
from app.posts import create_post_for_season
from app.schemas.admin_season import SeasonAdminPublic, SeasonCreate, SeasonUpdate

router = APIRouter(
    prefix="/animes/{anime_id}/seasons",
    tags=["author"],
    dependencies=[Depends(get_current_author)],
)

# Reads/writes keyed on an existing season only need season_id - anime_id is
# recoverable from the season itself, same flattening as episodes/packs/links.
season_router = APIRouter(
    prefix="/seasons", tags=["author"], dependencies=[Depends(get_current_author)]
)


def _to_public(season: Seasons, post_slug: str | None) -> SeasonAdminPublic:
    return SeasonAdminPublic(
        season_id=season.season_id,
        anime_id=season.anime_id,
        season_number=season.season_number,
        season_name=season.season_name,
        total_episodes=season.total_episodes,
        season_overview=season.season_overview,
        poster=resolve_image_urls(season.poster_source, season.poster_img, "poster"),
        rating=season.rating,
        season_tmdb_id=season.season_tmdb_id,
        season_rel_date=season.season_rel_date,
        status=season.status,
        post_slug=post_slug,
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

    return _to_public(season, post.slug)


@season_router.patch("/{season_id}")
def update_season(
    session: SessionDep, author: CurrentAuthor, season_id: int, body: SeasonUpdate
) -> SeasonAdminPublic:
    season = session.get(Seasons, season_id)
    if season is None:
        raise HTTPException(status_code=404, detail="Season not found")

    # Gate on the season's *current* status - an ongoing-tier author can
    # still be the one who flips it to completed, same as any other edit
    # they're allowed while it's still ongoing.
    require_anime_write_access(session, author, season.anime_id, season=season)

    updates = body.model_dump(exclude_unset=True)

    if "season_number" in updates and updates["season_number"] != season.season_number:
        existing = session.exec(
            select(Seasons).where(
                Seasons.anime_id == season.anime_id,
                Seasons.season_number == updates["season_number"],
            )
        ).first()
        if existing is not None:
            raise HTTPException(
                status_code=400,
                detail=f"Season {updates['season_number']} already exists for this anime",
            )

    for field, value in updates.items():
        setattr(season, field, value)

    session.add(season)
    session.commit()
    session.refresh(season)

    post = session.exec(select(Posts).where(Posts.season_id == season_id)).first()
    return _to_public(season, post.slug if post else None)


@season_router.delete("/{season_id}", status_code=204)
def delete_season(session: SessionDep, author: CurrentAuthor, season_id: int) -> None:
    """
    Deletes the season and everything under it - episodes, packs, their
    Content rows, every link, the post - via cascade_delete on the model
    relationships (see app/models.py). No manual cleanup needed.
    """
    season = session.get(Seasons, season_id)
    if season is None:
        raise HTTPException(status_code=404, detail="Season not found")

    require_anime_write_access(session, author, season.anime_id, season=season)

    session.delete(season)
    session.commit()
