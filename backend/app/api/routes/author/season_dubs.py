from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from app.api.deps import CurrentAuthor, SessionDep, get_current_author
from app.models import Languages, OttPlatforms, SeasonDubs, Seasons
from app.permissions import require_anime_write_access
from app.schemas.admin_season_dub import (
    SeasonDubAdminPublic,
    SeasonDubCreate,
    SeasonDubListPublic,
)

router = APIRouter(
    prefix="/seasons/{season_id}/dubs",
    tags=["author"],
    dependencies=[Depends(get_current_author)],
)


def _to_public(dub: SeasonDubs) -> SeasonDubAdminPublic:
    return SeasonDubAdminPublic(
        season_id=dub.season_id,
        ott_id=dub.ott_id,
        ott_name=dub.ott.ott_name,
        language_id=dub.language_id,
        language_name=dub.language.language_name,
    )


def _get_season_with_access(
    session: SessionDep, author: CurrentAuthor, season_id: int
) -> Seasons:
    season = session.get(Seasons, season_id)
    if season is None:
        raise HTTPException(status_code=404, detail="Season not found")
    require_anime_write_access(session, author, season.anime_id, season=season)
    return season


@router.get("/")
def list_season_dubs(
    session: SessionDep, author: CurrentAuthor, season_id: int
) -> SeasonDubListPublic:
    _get_season_with_access(session, author, season_id)
    dubs = session.exec(select(SeasonDubs).where(SeasonDubs.season_id == season_id)).all()
    return SeasonDubListPublic(data=[_to_public(d) for d in dubs])


@router.post("/", status_code=201)
def add_season_dub(
    session: SessionDep, author: CurrentAuthor, season_id: int, body: SeasonDubCreate
) -> SeasonDubAdminPublic:
    _get_season_with_access(session, author, season_id)

    if session.get(OttPlatforms, body.ott_id) is None:
        raise HTTPException(status_code=400, detail=f"No OTT platform with id {body.ott_id}")
    if session.get(Languages, body.language_id) is None:
        raise HTTPException(status_code=400, detail=f"No language with id {body.language_id}")

    existing = session.get(SeasonDubs, (season_id, body.ott_id, body.language_id))
    if existing is None:
        existing = SeasonDubs(
            season_id=season_id, ott_id=body.ott_id, language_id=body.language_id
        )
        session.add(existing)
        session.commit()
        session.refresh(existing)

    return _to_public(existing)


@router.delete("/{ott_id}/{language_id}", status_code=204)
def remove_season_dub(
    session: SessionDep, author: CurrentAuthor, season_id: int, ott_id: int, language_id: int
) -> None:
    _get_season_with_access(session, author, season_id)

    dub = session.get(SeasonDubs, (season_id, ott_id, language_id))
    if dub is None:
        raise HTTPException(status_code=404, detail="This dub is not set for this season")

    session.delete(dub)
    session.commit()
