from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import ColumnElement
from sqlmodel import col, func, select

from app.api.deps import CurrentAuthor, SessionDep, get_current_author
from app.media import resolve_image_urls
from app.models import (
    AgeRatings,
    Animes,
    AuthorAccessScope,
    AuthorAnimeAccess,
    Content,
    ContentContentType,
    Genres,
    Seasons,
)
from app.permissions import require_can_create_anime
from app.posts import create_post_for_anime
from app.schemas.admin_anime import (
    AnimeAdminListPublic,
    AnimeAdminPublic,
    AnimeAdminSummary,
    AnimeCreate,
)
from app.slugs import ensure_unique_slug, slugify

router = APIRouter(
    prefix="/animes", tags=["admin"], dependencies=[Depends(get_current_author)]
)


@router.get("/")
def list_animes(
    session: SessionDep,
    author: CurrentAuthor,
    q: str | None = None,
    anime_type: Literal["movie", "tv"] | None = Query(None, alias="type"),
    skip: int = 0,
    limit: int = 50,
) -> AnimeAdminListPublic:
    filters: list[ColumnElement[bool]] = []
    if q:
        filters.append(col(Animes.anime_name).ilike(f"%{q}%"))
    if anime_type:
        filters.append(col(Animes.type) == anime_type)

    # access_list authors only ever see anime explicitly granted to them.
    # all/ongoing (and superuser) see the full catalog - matches their
    # unrestricted write access to add new seasons under any anime, see
    # app.permissions.require_anime_write_access.
    if not author.is_superuser and author.access_scope == AuthorAccessScope.ACCESS_LIST:
        allowed_ids = select(AuthorAnimeAccess.anime_id).where(
            AuthorAnimeAccess.user_id == author.id
        )
        filters.append(col(Animes.anime_id).in_(allowed_ids))

    count = session.exec(select(func.count()).select_from(Animes).where(*filters)).one()

    season_count_subquery = (
        select(func.count())
        .select_from(Seasons)
        .where(Seasons.anime_id == Animes.anime_id)
        .scalar_subquery()
    )

    rows = session.exec(
        select(Animes, season_count_subquery)
        .where(*filters)
        .order_by(col(Animes.anime_id).desc())
        .offset(skip)
        .limit(limit)
    ).all()

    data = [
        AnimeAdminSummary(
            anime_id=anime.anime_id,
            slug=anime.slug,
            anime_name=anime.anime_name,
            type=anime.type,
            poster=resolve_image_urls(anime.poster_source, anime.poster_img, "poster"),
            rating=anime.rating,
            season_count=season_count,
        )
        for anime, season_count in rows
    ]
    return AnimeAdminListPublic(data=data, count=count)


@router.post("/")
def create_anime(
    session: SessionDep, author: CurrentAuthor, body: AnimeCreate
) -> AnimeAdminPublic:
    require_can_create_anime(author)

    if session.get(AgeRatings, body.age_id) is None:
        raise HTTPException(status_code=400, detail=f"No age rating with id {body.age_id}")

    genres: list[Genres] = []
    if body.genre_ids:
        genres = list(
            session.exec(select(Genres).where(col(Genres.genre_id).in_(body.genre_ids)))
        )
        found_ids = {g.genre_id for g in genres}
        missing_ids = set(body.genre_ids) - found_ids
        if missing_ids:
            raise HTTPException(
                status_code=400,
                detail=f"No genre with id(s): {', '.join(str(i) for i in sorted(missing_ids))}",
            )

    slug = ensure_unique_slug(session, slugify(body.anime_name), Animes, col(Animes.slug))

    # Content needs to exist before Animes (content_id is NOT NULL), but its
    # own respective_id can't be set until the Animes row has an id - insert
    # with a placeholder, flush to get an id, then backfill both directions.
    content = Content(content_type=ContentContentType.MOVIE, respective_id=None)
    session.add(content)
    session.flush()

    anime = Animes(
        slug=slug,
        anime_name=body.anime_name,
        backdrop_source=body.backdrop_source,
        backdrop_img=body.backdrop_img,
        poster_source=body.poster_source,
        poster_img=body.poster_img,
        age_id=body.age_id,
        overview=body.overview,
        duration=body.duration,
        rating=body.rating,
        type=body.type,
        links_update=datetime.now(UTC),
        content_id=content.id,
        anime_tmdb_id=body.anime_tmdb_id,
        anime_rel_date=body.anime_rel_date,
    )
    session.add(anime)
    session.flush()

    content.respective_id = anime.anime_id
    session.add(content)

    anime.genre = genres

    post_slug = None
    if body.type == "movie":
        post = create_post_for_anime(session, anime, author)
        post_slug = post.slug

    session.commit()
    session.refresh(anime)

    return AnimeAdminPublic(
        anime_id=anime.anime_id,
        slug=anime.slug,
        anime_name=anime.anime_name,
        type=anime.type,
        poster=resolve_image_urls(anime.poster_source, anime.poster_img, "poster"),
        backdrop=resolve_image_urls(anime.backdrop_source, anime.backdrop_img, "backdrop"),
        overview=anime.overview,
        duration=anime.duration,
        rating=anime.rating,
        age_id=anime.age_id,
        anime_tmdb_id=anime.anime_tmdb_id,
        anime_rel_date=anime.anime_rel_date,
        genres=[g.genre_name for g in anime.genre],
        post_slug=post_slug,
    )
