from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, select

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import LinkShorteners
from app.schemas.admin_shortener import (
    ShortenerAdminListPublic,
    ShortenerAdminPublic,
    ShortenerCreate,
    ShortenerUpdate,
)

router = APIRouter(
    prefix="/shorteners", tags=["admin"], dependencies=[Depends(get_current_active_superuser)]
)


def _to_public(shortener: LinkShorteners) -> ShortenerAdminPublic:
    assert shortener.id is not None
    return ShortenerAdminPublic(
        id=shortener.id,
        name=shortener.name,
        slug=shortener.slug,
        api_url_template=shortener.api_url_template,
        quick_url_template=shortener.quick_url_template,
        how_to_video_url=shortener.how_to_video_url,
        message=shortener.message,
        logo_url=shortener.logo_url,
        is_enabled=shortener.is_enabled,
        sort_order=shortener.sort_order,
    )


def _check_slug_free(session: SessionDep, slug: str, exclude_id: int | None = None) -> None:
    existing = session.exec(
        select(LinkShorteners).where(LinkShorteners.slug == slug)
    ).first()
    if existing is not None and existing.id != exclude_id:
        raise HTTPException(
            status_code=400, detail=f"A shortener with slug '{slug}' already exists"
        )


@router.get("/")
def list_shorteners(session: SessionDep) -> ShortenerAdminListPublic:
    shorteners = session.exec(
        select(LinkShorteners).order_by(col(LinkShorteners.sort_order).asc())
    ).all()
    return ShortenerAdminListPublic(data=[_to_public(s) for s in shorteners])


@router.post("/", status_code=201)
def create_shortener(
    session: SessionDep, body: ShortenerCreate
) -> ShortenerAdminPublic:
    _check_slug_free(session, body.slug)

    shortener = LinkShorteners(**body.model_dump())
    session.add(shortener)
    session.commit()
    session.refresh(shortener)
    return _to_public(shortener)


@router.patch("/{shortener_id}")
def update_shortener(
    session: SessionDep, shortener_id: int, body: ShortenerUpdate
) -> ShortenerAdminPublic:
    shortener = session.get(LinkShorteners, shortener_id)
    if shortener is None:
        raise HTTPException(status_code=404, detail="Shortener not found")

    updates = body.model_dump(exclude_unset=True)
    if "slug" in updates:
        _check_slug_free(session, updates["slug"], exclude_id=shortener_id)

    for field, value in updates.items():
        setattr(shortener, field, value)

    session.add(shortener)
    session.commit()
    session.refresh(shortener)
    return _to_public(shortener)


@router.delete("/{shortener_id}", status_code=204)
def delete_shortener(session: SessionDep, shortener_id: int) -> None:
    shortener = session.get(LinkShorteners, shortener_id)
    if shortener is None:
        raise HTTPException(status_code=404, detail="Shortener not found")
    session.delete(shortener)
    session.commit()
