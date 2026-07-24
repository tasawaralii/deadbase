from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app.api.deps import SessionDep, get_current_active_superuser, get_current_author
from app.models import AgeRatings, Animes
from app.schemas.admin_age_rating import (
    AgeRatingAdminListPublic,
    AgeRatingAdminPublic,
    AgeRatingCreate,
    AgeRatingUpdate,
)

# Read is author-accessible (needed to populate the age-rating picker when
# creating/editing an anime) - writes are superuser-only, same split as
# every other reference table here.
router = APIRouter(
    prefix="/age-ratings", tags=["admin"], dependencies=[Depends(get_current_author)]
)


def _to_public(row: AgeRatings) -> AgeRatingAdminPublic:
    return AgeRatingAdminPublic(age_id=row.age_id, age_name=row.age_name, age_des=row.age_des)


@router.get("/")
def list_age_ratings(session: SessionDep) -> AgeRatingAdminListPublic:
    rows = session.exec(select(AgeRatings)).all()
    return AgeRatingAdminListPublic(data=[_to_public(r) for r in rows])


@router.post("/", status_code=201, dependencies=[Depends(get_current_active_superuser)])
def create_age_rating(session: SessionDep, body: AgeRatingCreate) -> AgeRatingAdminPublic:
    row = AgeRatings(**body.model_dump())
    session.add(row)
    session.commit()
    session.refresh(row)
    return _to_public(row)


@router.patch("/{age_id}", dependencies=[Depends(get_current_active_superuser)])
def update_age_rating(
    session: SessionDep, age_id: int, body: AgeRatingUpdate
) -> AgeRatingAdminPublic:
    row = session.get(AgeRatings, age_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Age rating not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(row, field, value)

    session.add(row)
    session.commit()
    session.refresh(row)
    return _to_public(row)


@router.delete(
    "/{age_id}", status_code=204, dependencies=[Depends(get_current_active_superuser)]
)
def delete_age_rating(session: SessionDep, age_id: int) -> None:
    row = session.get(AgeRatings, age_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Age rating not found")

    in_use = session.exec(
        select(func.count()).select_from(Animes).where(Animes.age_id == age_id)
    ).one()
    if in_use:
        raise HTTPException(
            status_code=400,
            detail=f"Still used by {in_use} anime - reassign or delete those first",
        )

    session.delete(row)
    session.commit()
