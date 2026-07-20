from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, select

from app.api.deps import CurrentAuthor, SessionDep, get_current_author
from app.media import resolve_image_urls
from app.models import Content, ContentContentType, Episodes, Seasons
from app.permissions import require_anime_write_access
from app.schemas.admin_episode import (
    EpisodeAdminPublic,
    EpisodeBatchCreate,
    EpisodeBatchPublic,
    EpisodeUpdate,
)

router = APIRouter(
    prefix="/seasons/{season_id}/episodes",
    tags=["author"],
    dependencies=[Depends(get_current_author)],
)


def _to_public(episode: Episodes) -> EpisodeAdminPublic:
    return EpisodeAdminPublic(
        episode_id=episode.episode_id,
        season_id=episode.season_id,
        content_id=episode.content_id,
        episode_number=episode.episode_number,
        episode_name=episode.episode_name,
        overview=episode.overview,
        img=resolve_image_urls("tmdb", episode.img, "backdrop"),
        air_date=episode.air_date,
        episode_runtime=episode.episode_runtime,
        episode_rating=episode.episode_rating,
        episode_tmdb_id=episode.episode_tmdb_id,
        note=episode.note,
    )


@router.get("/")
def list_episodes(
    session: SessionDep, author: CurrentAuthor, season_id: int
) -> EpisodeBatchPublic:
    season = session.get(Seasons, season_id)
    if season is None:
        raise HTTPException(status_code=404, detail="Season not found")

    require_anime_write_access(session, author, season.anime_id, season=season)

    episodes = session.exec(
        select(Episodes)
        .where(Episodes.season_id == season_id)
        .order_by(col(Episodes.episode_number).asc())
    ).all()
    return EpisodeBatchPublic(data=[_to_public(e) for e in episodes])


@router.post("/")
def create_episodes(
    session: SessionDep, author: CurrentAuthor, season_id: int, body: EpisodeBatchCreate
) -> EpisodeBatchPublic:
    season = session.get(Seasons, season_id)
    if season is None:
        raise HTTPException(status_code=404, detail="Season not found")

    # anime_id lives on the season row - no need for the caller to carry it
    # separately alongside season_id.
    require_anime_write_access(session, author, season.anime_id, season=season)

    if not body.episodes:
        raise HTTPException(status_code=400, detail="At least one episode is required")

    submitted_numbers = [item.episode_number for item in body.episodes]
    if len(submitted_numbers) != len(set(submitted_numbers)):
        raise HTTPException(
            status_code=400, detail="Duplicate episode_number(s) within this batch"
        )

    existing_numbers = set(
        session.exec(
            select(Episodes.episode_number).where(Episodes.season_id == season_id)
        )
    )
    collisions = existing_numbers & set(submitted_numbers)
    if collisions:
        raise HTTPException(
            status_code=400,
            detail=(
                "Episode number(s) already exist for this season: "
                f"{', '.join(str(n) for n in sorted(collisions))}"
            ),
        )

    created: list[Episodes] = []
    for item in body.episodes:
        # Same two-step Content dance as Animes - content_id is NOT NULL but
        # can't be known until the row it points back to has an id.
        content = Content(content_type=ContentContentType.EPISODE, respective_id=None)
        session.add(content)
        session.flush()

        episode = Episodes(
            season_id=season_id,
            episode_number=item.episode_number,
            content_id=content.id,
            episode_tmdb_id=item.episode_tmdb_id,
            episode_name=item.episode_name,
            note=item.note,
            episode_runtime=item.episode_runtime,
            episode_rating=item.episode_rating,
            img=item.img,
            air_date=item.air_date,
            overview=item.overview,
        )
        session.add(episode)
        session.flush()

        content.respective_id = episode.episode_id
        session.add(content)
        created.append(episode)

    session.commit()
    for episode in created:
        session.refresh(episode)

    return EpisodeBatchPublic(data=[_to_public(e) for e in created])


@router.patch("/{episode_id}")
def update_episode(
    session: SessionDep,
    author: CurrentAuthor,
    season_id: int,
    episode_id: int,
    body: EpisodeUpdate,
) -> EpisodeAdminPublic:
    season = session.get(Seasons, season_id)
    if season is None:
        raise HTTPException(status_code=404, detail="Season not found")

    require_anime_write_access(session, author, season.anime_id, season=season)

    episode = session.get(Episodes, episode_id)
    if episode is None or episode.season_id != season_id:
        raise HTTPException(status_code=404, detail="Episode not found in this season")

    updates = body.model_dump(exclude_unset=True)

    if "episode_number" in updates and updates["episode_number"] != episode.episode_number:
        existing = session.exec(
            select(Episodes).where(
                Episodes.season_id == season_id,
                Episodes.episode_number == updates["episode_number"],
            )
        ).first()
        if existing is not None:
            raise HTTPException(
                status_code=400,
                detail=f"Episode {updates['episode_number']} already exists for this season",
            )

    for field, value in updates.items():
        setattr(episode, field, value)

    session.add(episode)
    session.commit()
    session.refresh(episode)

    return _to_public(episode)
