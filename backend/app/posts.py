from datetime import UTC, datetime

from sqlmodel import Session, col

from app.media import resolve_image_urls
from app.models import Animes, Posts, PostStatus, Seasons, User
from app.slugs import ensure_unique_slug, slugify


def _create_post(
    session: Session,
    *,
    anime_id: int | None,
    season_id: int | None,
    title: str,
    backdrop_source: str,
    backdrop_img: str | None,
    author: User,
) -> Posts:
    post_slug = ensure_unique_slug(session, slugify(title), Posts, col(Posts.slug))
    backdrop_url = resolve_image_urls(backdrop_source, backdrop_img, "backdrop").high

    post = Posts(
        anime_id=anime_id,
        season_id=season_id,
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


def create_post_for_anime(session: Session, anime: Animes, author: User) -> Posts:
    year = anime.anime_rel_date.year if anime.anime_rel_date else None
    title = f"{anime.anime_name} ({year}) Movie" if year else f"{anime.anime_name} Movie"
    return _create_post(
        session,
        anime_id=anime.anime_id,
        season_id=None,
        title=title,
        backdrop_source=anime.backdrop_source,
        backdrop_img=anime.backdrop_img,
        author=author,
    )


def create_post_for_season(
    session: Session, anime: Animes, season: Seasons, author: User
) -> Posts:
    year = season.season_rel_date.year if season.season_rel_date else (
        anime.anime_rel_date.year if anime.anime_rel_date else None
    )
    title = f"{anime.anime_name} Season {season.season_number}"
    if year:
        title = f"{title} ({year})"
    # Seasons have no backdrop of their own - always fall back to the
    # parent anime's, per the design ("backdrop of movie or season - anime
    # will be set as blog image").
    return _create_post(
        session,
        anime_id=None,
        season_id=season.season_id,
        title=title,
        backdrop_source=anime.backdrop_source,
        backdrop_img=anime.backdrop_img,
        author=author,
    )
