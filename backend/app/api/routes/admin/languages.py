from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import Languages, SeasonDubs
from app.schemas.admin_language import (
    LanguageAdminListPublic,
    LanguageAdminPublic,
    LanguageCreate,
    LanguageUpdate,
)

router = APIRouter(
    prefix="/languages", tags=["admin"], dependencies=[Depends(get_current_active_superuser)]
)


def _to_public(row: Languages) -> LanguageAdminPublic:
    return LanguageAdminPublic(
        language_id=row.language_id,
        language_sid=row.language_sid,
        language_name=row.language_name,
    )


def _check_sid_free(
    session: SessionDep, language_sid: str, exclude_id: int | None = None
) -> None:
    existing = session.exec(
        select(Languages).where(Languages.language_sid == language_sid)
    ).first()
    if existing is not None and existing.language_id != exclude_id:
        raise HTTPException(
            status_code=400,
            detail=f"A language with language_sid '{language_sid}' already exists",
        )


@router.get("/")
def list_languages(session: SessionDep) -> LanguageAdminListPublic:
    rows = session.exec(select(Languages)).all()
    return LanguageAdminListPublic(data=[_to_public(r) for r in rows])


@router.post("/", status_code=201)
def create_language(session: SessionDep, body: LanguageCreate) -> LanguageAdminPublic:
    _check_sid_free(session, body.language_sid)

    row = Languages(**body.model_dump())
    session.add(row)
    session.commit()
    session.refresh(row)
    return _to_public(row)


@router.patch("/{language_id}")
def update_language(
    session: SessionDep, language_id: int, body: LanguageUpdate
) -> LanguageAdminPublic:
    row = session.get(Languages, language_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Language not found")

    updates = body.model_dump(exclude_unset=True)
    if updates.get("language_sid"):
        _check_sid_free(session, updates["language_sid"], exclude_id=language_id)

    for field, value in updates.items():
        setattr(row, field, value)

    session.add(row)
    session.commit()
    session.refresh(row)
    return _to_public(row)


@router.delete("/{language_id}", status_code=204)
def delete_language(session: SessionDep, language_id: int) -> None:
    row = session.get(Languages, language_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Language not found")

    in_use = session.exec(
        select(func.count())
        .select_from(SeasonDubs)
        .where(SeasonDubs.language_id == language_id)
    ).one()
    if in_use:
        raise HTTPException(
            status_code=400,
            detail=f"Still used by {in_use} season dub entr{'y' if in_use == 1 else 'ies'}",
        )

    session.delete(row)
    session.commit()
