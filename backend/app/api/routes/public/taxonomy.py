from fastapi import APIRouter
from sqlmodel import col, select

from app.api.deps import SessionDep
from app.models import Genres, Tags
from app.schemas.common import GenrePublic, TagPublic

router = APIRouter()


@router.get("/tags")
def list_tags(session: SessionDep) -> list[TagPublic]:
    tags = session.exec(select(Tags).order_by(col(Tags.name).asc())).all()
    return [TagPublic(name=t.name, slug=t.slug) for t in tags]


@router.get("/genres")
def list_genres(session: SessionDep) -> list[GenrePublic]:
    genres = session.exec(select(Genres).order_by(col(Genres.genre_name).asc())).all()
    return [GenrePublic(name=g.genre_name, slug=g.genre_sid) for g in genres]
