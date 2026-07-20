from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import OttPlatforms, SeasonDubs
from app.schemas.admin_ott_platform import (
    OttPlatformAdminListPublic,
    OttPlatformAdminPublic,
    OttPlatformCreate,
    OttPlatformUpdate,
)

router = APIRouter(
    prefix="/ott-platforms", tags=["admin"], dependencies=[Depends(get_current_active_superuser)]
)


def _to_public(row: OttPlatforms) -> OttPlatformAdminPublic:
    return OttPlatformAdminPublic(ott_id=row.ott_id, ott_sid=row.ott_sid, ott_name=row.ott_name)


def _check_sid_free(session: SessionDep, ott_sid: str, exclude_id: int | None = None) -> None:
    existing = session.exec(select(OttPlatforms).where(OttPlatforms.ott_sid == ott_sid)).first()
    if existing is not None and existing.ott_id != exclude_id:
        raise HTTPException(
            status_code=400, detail=f"An OTT platform with ott_sid '{ott_sid}' already exists"
        )


@router.get("/")
def list_ott_platforms(session: SessionDep) -> OttPlatformAdminListPublic:
    rows = session.exec(select(OttPlatforms)).all()
    return OttPlatformAdminListPublic(data=[_to_public(r) for r in rows])


@router.post("/", status_code=201)
def create_ott_platform(session: SessionDep, body: OttPlatformCreate) -> OttPlatformAdminPublic:
    _check_sid_free(session, body.ott_sid)

    row = OttPlatforms(**body.model_dump())
    session.add(row)
    session.commit()
    session.refresh(row)
    return _to_public(row)


@router.patch("/{ott_id}")
def update_ott_platform(
    session: SessionDep, ott_id: int, body: OttPlatformUpdate
) -> OttPlatformAdminPublic:
    row = session.get(OttPlatforms, ott_id)
    if row is None:
        raise HTTPException(status_code=404, detail="OTT platform not found")

    updates = body.model_dump(exclude_unset=True)
    if updates.get("ott_sid"):
        _check_sid_free(session, updates["ott_sid"], exclude_id=ott_id)

    for field, value in updates.items():
        setattr(row, field, value)

    session.add(row)
    session.commit()
    session.refresh(row)
    return _to_public(row)


@router.delete("/{ott_id}", status_code=204)
def delete_ott_platform(session: SessionDep, ott_id: int) -> None:
    row = session.get(OttPlatforms, ott_id)
    if row is None:
        raise HTTPException(status_code=404, detail="OTT platform not found")

    in_use = session.exec(
        select(func.count()).select_from(SeasonDubs).where(SeasonDubs.ott_id == ott_id)
    ).one()
    if in_use:
        raise HTTPException(
            status_code=400,
            detail=f"Still used by {in_use} season dub entr{'y' if in_use == 1 else 'ies'}",
        )

    session.delete(row)
    session.commit()
