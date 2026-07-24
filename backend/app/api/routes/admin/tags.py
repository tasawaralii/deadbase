from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from app.api.deps import SessionDep, get_current_active_superuser, get_current_author
from app.models import Tags
from app.schemas.admin_tag import (
    TagAdminListPublic,
    TagAdminPublic,
    TagCreate,
    TagUpdate,
)

# Deleting a tag is safe even if in use - PostTags cascades (removes it
# from any post's tag list), no RESTRICT to work around. Read is author-
# accessible (needed for the tag picker on post edit) - writes are
# superuser-only.
router = APIRouter(prefix="/tags", tags=["admin"], dependencies=[Depends(get_current_author)])


def _to_public(row: Tags) -> TagAdminPublic:
    assert row.id is not None
    return TagAdminPublic(id=row.id, slug=row.slug, name=row.name)


def _check_slug_free(session: SessionDep, slug: str, exclude_id: int | None = None) -> None:
    existing = session.exec(select(Tags).where(Tags.slug == slug)).first()
    if existing is not None and existing.id != exclude_id:
        raise HTTPException(status_code=400, detail=f"A tag with slug '{slug}' already exists")


@router.get("/")
def list_tags(session: SessionDep) -> TagAdminListPublic:
    rows = session.exec(select(Tags)).all()
    return TagAdminListPublic(data=[_to_public(r) for r in rows])


@router.post("/", status_code=201, dependencies=[Depends(get_current_active_superuser)])
def create_tag(session: SessionDep, body: TagCreate) -> TagAdminPublic:
    _check_slug_free(session, body.slug)

    row = Tags(**body.model_dump())
    session.add(row)
    session.commit()
    session.refresh(row)
    return _to_public(row)


@router.patch("/{tag_id}", dependencies=[Depends(get_current_active_superuser)])
def update_tag(session: SessionDep, tag_id: int, body: TagUpdate) -> TagAdminPublic:
    row = session.get(Tags, tag_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Tag not found")

    updates = body.model_dump(exclude_unset=True)
    if updates.get("slug"):
        _check_slug_free(session, updates["slug"], exclude_id=tag_id)

    for field, value in updates.items():
        setattr(row, field, value)

    session.add(row)
    session.commit()
    session.refresh(row)
    return _to_public(row)


@router.delete(
    "/{tag_id}", status_code=204, dependencies=[Depends(get_current_active_superuser)]
)
def delete_tag(session: SessionDep, tag_id: int) -> None:
    row = session.get(Tags, tag_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    session.delete(row)
    session.commit()
