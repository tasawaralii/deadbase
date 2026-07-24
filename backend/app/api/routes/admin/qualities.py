from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, select

from app.api.deps import SessionDep, get_current_active_superuser, get_current_author
from app.models import Qualities
from app.schemas.admin_quality import (
    QualityAdminListPublic,
    QualityAdminPublic,
    QualityCreate,
    QualityUpdate,
)

# Deleting a quality is safe even if in use - Links.quality_id is SET NULL,
# not RESTRICT - existing links just lose their quality tag, not blocked.
# Read is author-accessible (needed to manually override a link's quality) -
# writes are superuser-only.
router = APIRouter(
    prefix="/qualities", tags=["admin"], dependencies=[Depends(get_current_author)]
)


def _to_public(row: Qualities) -> QualityAdminPublic:
    return QualityAdminPublic(
        quality_id=row.quality_id,
        quality_resolution=row.quality_resolution,
        is_hevc=row.is_hevc,
        is_hq=row.is_hq,
        quality_order=row.quality_order,
        quality_name=row.quality_name,
    )


@router.get("/")
def list_qualities(session: SessionDep) -> QualityAdminListPublic:
    rows = session.exec(select(Qualities).order_by(col(Qualities.quality_order).asc())).all()
    return QualityAdminListPublic(data=[_to_public(r) for r in rows])


@router.post("/", status_code=201, dependencies=[Depends(get_current_active_superuser)])
def create_quality(session: SessionDep, body: QualityCreate) -> QualityAdminPublic:
    row = Qualities(**body.model_dump())
    session.add(row)
    session.commit()
    session.refresh(row)
    return _to_public(row)


@router.patch("/{quality_id}", dependencies=[Depends(get_current_active_superuser)])
def update_quality(
    session: SessionDep, quality_id: int, body: QualityUpdate
) -> QualityAdminPublic:
    row = session.get(Qualities, quality_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Quality not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(row, field, value)

    session.add(row)
    session.commit()
    session.refresh(row)
    return _to_public(row)


@router.delete(
    "/{quality_id}", status_code=204, dependencies=[Depends(get_current_active_superuser)]
)
def delete_quality(session: SessionDep, quality_id: int) -> None:
    row = session.get(Qualities, quality_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Quality not found")
    session.delete(row)
    session.commit()
