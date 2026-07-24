from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, func, select

from app.api.deps import CurrentAuthor, SessionDep, get_current_author
from app.models import Content, ContentContentType, Links, Packs, Seasons
from app.permissions import require_anime_write_access
from app.schemas.admin_pack import (
    PackAdminPublic,
    PackCreate,
    PackListPublic,
    PackUpdate,
)

router = APIRouter(
    prefix="/seasons/{season_id}/packs",
    tags=["author"],
    dependencies=[Depends(get_current_author)],
)


def _to_public(pack: Packs, link_count: int) -> PackAdminPublic:
    return PackAdminPublic(
        pack_id=pack.pack_id,
        season_id=pack.season_id,
        content_id=pack.content_id,
        pack_name=pack.pack_name,
        start_ep=pack.start_ep,
        end_ep=pack.end_ep,
        link_count=link_count,
    )


def _count_links(session: SessionDep, content_id: int) -> int:
    return session.exec(
        select(func.count()).select_from(Links).where(Links.content_id == content_id)
    ).one()


@router.get("/")
def list_packs(
    session: SessionDep, author: CurrentAuthor, season_id: int
) -> PackListPublic:
    season = session.get(Seasons, season_id)
    if season is None:
        raise HTTPException(status_code=404, detail="Season not found")
    require_anime_write_access(session, author, season.anime_id, season=season)

    link_count_subq = (
        select(func.count(col(Links.link_id)))
        .where(Links.content_id == Packs.content_id)
        .scalar_subquery()
    )
    packs = session.exec(
        select(Packs, link_count_subq).where(Packs.season_id == season_id)
    ).all()
    return PackListPublic(data=[_to_public(p, count) for p, count in packs])


@router.post("/")
def create_pack(
    session: SessionDep, author: CurrentAuthor, season_id: int, body: PackCreate
) -> PackAdminPublic:
    season = session.get(Seasons, season_id)
    if season is None:
        raise HTTPException(status_code=404, detail="Season not found")
    require_anime_write_access(session, author, season.anime_id, season=season)

    if body.end_ep < body.start_ep:
        raise HTTPException(status_code=400, detail="end_ep must be >= start_ep")

    existing = session.exec(
        select(Packs).where(
            Packs.season_id == season_id,
            Packs.start_ep == body.start_ep,
            Packs.end_ep == body.end_ep,
        )
    ).first()
    if existing is not None:
        raise HTTPException(
            status_code=400,
            detail=f"A pack for episodes {body.start_ep}-{body.end_ep} already exists",
        )

    # Same two-step Content dance as Animes/Episodes.
    content = Content(content_type=ContentContentType.PACK, respective_id=None)
    session.add(content)
    session.flush()

    pack = Packs(
        season_id=season_id,
        pack_name=body.pack_name,
        start_ep=body.start_ep,
        end_ep=body.end_ep,
        content_id=content.id,
    )
    session.add(pack)
    session.flush()

    content.respective_id = pack.pack_id
    session.add(content)

    session.commit()
    session.refresh(pack)
    return _to_public(pack, link_count=0)


@router.patch("/{pack_id}")
def update_pack(
    session: SessionDep,
    author: CurrentAuthor,
    season_id: int,
    pack_id: int,
    body: PackUpdate,
) -> PackAdminPublic:
    season = session.get(Seasons, season_id)
    if season is None:
        raise HTTPException(status_code=404, detail="Season not found")

    require_anime_write_access(session, author, season.anime_id, season=season)

    pack = session.get(Packs, pack_id)
    if pack is None or pack.season_id != season_id:
        raise HTTPException(status_code=404, detail="Pack not found in this season")

    updates = body.model_dump(exclude_unset=True)

    new_start = updates.get("start_ep", pack.start_ep)
    new_end = updates.get("end_ep", pack.end_ep)
    if new_end < new_start:
        raise HTTPException(status_code=400, detail="end_ep must be >= start_ep")

    if "start_ep" in updates or "end_ep" in updates:
        existing = session.exec(
            select(Packs).where(
                Packs.season_id == season_id,
                Packs.pack_id != pack_id,
                Packs.start_ep == new_start,
                Packs.end_ep == new_end,
            )
        ).first()
        if existing is not None:
            raise HTTPException(
                status_code=400,
                detail=f"A pack for episodes {new_start}-{new_end} already exists",
            )

    for field, value in updates.items():
        setattr(pack, field, value)

    session.add(pack)
    session.commit()
    session.refresh(pack)
    return _to_public(pack, _count_links(session, pack.content_id))


@router.delete("/{pack_id}", status_code=204)
def delete_pack(
    session: SessionDep, author: CurrentAuthor, season_id: int, pack_id: int
) -> None:
    """Deletes the pack, its Content row, and every link on it - via
    cascade_delete on the model relationships (see app/models.py)."""
    season = session.get(Seasons, season_id)
    if season is None:
        raise HTTPException(status_code=404, detail="Season not found")

    require_anime_write_access(session, author, season.anime_id, season=season)

    pack = session.get(Packs, pack_id)
    if pack is None or pack.season_id != season_id:
        raise HTTPException(status_code=404, detail="Pack not found in this season")

    session.delete(pack)
    session.commit()
