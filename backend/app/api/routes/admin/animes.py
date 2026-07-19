from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, select

from app.api.deps import CurrentAuthor, SessionDep, get_current_author
from app.media import resolve_image_urls
from app.models import (
    AgeRatings,
    Animes,
    AuthorAccessScope,
    Content,
    ContentContentType,
    Genres,
    Posts,
    PostStatus,
    User,
)
from app.schemas.admin_anime import AnimeAdminPublic, AnimeCreate
from app.slugs import ensure_unique_slug, slugify

router = APIRouter(
    prefix="/animes", tags=["admin"], dependencies=[Depends(get_current_author)]
)


def _create_post_for_anime(session: SessionDep, anime: Animes, author: User) -> Posts:
    year = anime.anime_rel_date.year if anime.anime_rel_date else None
    title = f"{anime.anime_name} ({year}) Movie" if year else f"{anime.anime_name} Movie"
    post_slug = ensure_unique_slug(session, slugify(title), Posts, col(Posts.slug))
    backdrop_url = resolve_image_urls(
        anime.backdrop_source, anime.backdrop_img, "backdrop"
    ).high

    post = Posts(
        anime_id=anime.anime_id,
        title=title,
        slug=post_slug,
        backdrop_img=backdrop_url or None,
        status=PostStatus.ONGOING,
        author_id=author.id,
        last_updated=datetime.now(UTC),
    )
    session.add(post)
    session.flush()
    return post


@router.post("/")
def create_anime(
    session: SessionDep, author: CurrentAuthor, body: AnimeCreate
) -> AnimeAdminPublic:
    # access_list authors only manage anime already assigned to them - net
    # new content creation is out of scope for that tier.
    if not author.is_superuser and author.access_scope == AuthorAccessScope.ACCESS_LIST:
        raise HTTPException(
            status_code=403,
            detail="Your account can only manage anime already assigned to it",
        )

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
        post = _create_post_for_anime(session, anime, author)
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
