from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from app.api.deps import SessionDep, get_current_active_superuser, get_current_author
from app.models import Genres
from app.schemas.admin_genre import (
    GenreAdminListPublic,
    GenreAdminPublic,
    GenreCreate,
    GenreUpdate,
)

# Deleting a genre is safe even if in use - anime_genres cascades (removes
# it from any anime's genre list), no RESTRICT to work around. Read is
# author-accessible (needed for the genre picker on anime create/edit) -
# writes are superuser-only.
router = APIRouter(prefix="/genres", tags=["admin"], dependencies=[Depends(get_current_author)])


def _to_public(row: Genres) -> GenreAdminPublic:
    return GenreAdminPublic(
        genre_id=row.genre_id, genre_name=row.genre_name, genre_sid=row.genre_sid
    )


def _check_sid_free(session: SessionDep, genre_sid: str, exclude_id: int | None = None) -> None:
    existing = session.exec(select(Genres).where(Genres.genre_sid == genre_sid)).first()
    if existing is not None and existing.genre_id != exclude_id:
        raise HTTPException(
            status_code=400, detail=f"A genre with genre_sid '{genre_sid}' already exists"
        )


@router.get("/")
def list_genres(session: SessionDep) -> GenreAdminListPublic:
    rows = session.exec(select(Genres)).all()
    return GenreAdminListPublic(data=[_to_public(r) for r in rows])


@router.post("/", status_code=201, dependencies=[Depends(get_current_active_superuser)])
def create_genre(session: SessionDep, body: GenreCreate) -> GenreAdminPublic:
    _check_sid_free(session, body.genre_sid)

    row = Genres(**body.model_dump())
    session.add(row)
    session.commit()
    session.refresh(row)
    return _to_public(row)


@router.patch("/{genre_id}", dependencies=[Depends(get_current_active_superuser)])
def update_genre(session: SessionDep, genre_id: int, body: GenreUpdate) -> GenreAdminPublic:
    row = session.get(Genres, genre_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Genre not found")

    updates = body.model_dump(exclude_unset=True)
    if updates.get("genre_sid"):
        _check_sid_free(session, updates["genre_sid"], exclude_id=genre_id)

    for field, value in updates.items():
        setattr(row, field, value)

    session.add(row)
    session.commit()
    session.refresh(row)
    return _to_public(row)


@router.delete(
    "/{genre_id}", status_code=204, dependencies=[Depends(get_current_active_superuser)]
)
def delete_genre(session: SessionDep, genre_id: int) -> None:
    row = session.get(Genres, genre_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Genre not found")
    session.delete(row)
    session.commit()
