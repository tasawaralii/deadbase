import re
from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import ColumnElement
from sqlalchemy.orm import aliased, selectinload
from sqlmodel import col, func, select

from app.api.deps import SessionDep
from app.api.routes.public.anime import build_anime_detail
from app.api.routes.public.season import build_season_detail
from app.models import (
    Animes,
    Comments,
    CommentStatus,
    Genres,
    Posts,
    PostStatus,
    PostTags,
    Seasons,
    Tags,
)
from app.schemas.post import (
    CommentCreate,
    CommentPublic,
    PostDetail,
    PostListPublic,
    PostSummary,
)

router = APIRouter()

# Ported from the old blog's comment handler: URLs get held for review, Cyrillic
# text and this known spam-bot honeypot domain get rejected outright.
SPAM_TERMS = ("https://", "http://", "url")
BLOCKED_EMAIL_DOMAINS = ("testing-your-form.info",)
CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")


def _comment_public(comment: Comments) -> CommentPublic:
    return CommentPublic(
        id=comment.id,
        parent_id=comment.parent_id,
        author_name=comment.author_name,
        author_url=comment.author_url,
        body=comment.body,
        created_at=comment.created_at,
    )


@router.get("/posts")
def list_posts(
    session: SessionDep,
    q: str | None = None,
    status: PostStatus | None = None,
    post_type: Literal["movie", "tv"] | None = Query(None, alias="type"),
    genre: str | None = None,
    tag: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> PostListPublic:
    ParentAnime = aliased(Animes)  # noqa: N806

    conditions: list[ColumnElement[bool]] = []
    if q:
        conditions.append(col(Posts.title).ilike(f"%{q}%"))
    if status:
        conditions.append(col(Posts.status) == status)
    if post_type == "movie":
        conditions.append(col(Posts.anime_id).is_not(None))
    elif post_type == "tv":
        conditions.append(col(Posts.season_id).is_not(None))
    if genre:
        conditions.append(
            Animes.genre.any(Genres.genre_sid == genre)  # type: ignore[attr-defined]
            | ParentAnime.genre.any(Genres.genre_sid == genre)  # type: ignore[attr-defined]
        )
    if tag:
        conditions.append(
            select(PostTags.post_id)
            .join(Tags, col(Tags.id) == PostTags.tag_id)
            .where(PostTags.post_id == Posts.id, Tags.slug == tag)
            .exists()
        )

    comment_count_subq = (
        select(func.count(col(Comments.id)))
        .where(
            Comments.post_id == Posts.id,
            Comments.status == CommentStatus.APPROVED,
        )
        .scalar_subquery()
    )

    base_query = (
        select(Posts)
        .outerjoin(Animes, Posts.anime_id == Animes.anime_id)  # type: ignore[arg-type]
        .outerjoin(Seasons, Posts.season_id == Seasons.season_id)  # type: ignore[arg-type]
        .outerjoin(ParentAnime, Seasons.anime_id == ParentAnime.anime_id)  # type: ignore[arg-type]
        .where(*conditions)
    )

    total = session.exec(
        select(func.count()).select_from(base_query.subquery())
    ).one()

    rows = session.exec(
        select(  # type: ignore[call-overload]
            Posts, Animes, Seasons, ParentAnime, comment_count_subq
        )
        .outerjoin(Animes, Posts.anime_id == Animes.anime_id)
        .outerjoin(Seasons, Posts.season_id == Seasons.season_id)
        .outerjoin(ParentAnime, Seasons.anime_id == ParentAnime.anime_id)
        .where(*conditions)
        .order_by(col(Posts.last_updated).desc())
        .offset((page - 1) * limit)
        .limit(limit)
    ).all()

    post_ids = [post.id for post, *_ in rows if post.id is not None]
    tag_rows = session.exec(
        select(PostTags.post_id, Tags.name)
        .join(Tags, col(Tags.id) == PostTags.tag_id)
        .where(col(PostTags.post_id).in_(post_ids))
    ).all()
    tags_by_post: dict[int, list[str]] = {}
    for post_id, tag_name in tag_rows:
        tags_by_post.setdefault(post_id, []).append(tag_name)

    data = []
    for post, movie_anime, season, parent_anime, comment_count in rows:
        anime = movie_anime or parent_anime
        assert anime is not None
        data.append(
            PostSummary(
                slug=post.slug,
                title=post.title,
                backdrop_img=post.backdrop_img,
                status=post.status,
                sticky=post.sticky,
                views=post.views,
                last_updated=post.last_updated,
                tags=tags_by_post.get(post.id, []) if post.id is not None else [],
                comment_count=comment_count,
                anime_slug=anime.slug,
                anime_name=anime.anime_name,
                season_number=season.season_number if season else None,
                type="movie" if movie_anime else "tv",
            )
        )

    return PostListPublic(data=data, page=page, limit=limit, count=total)


@router.get("/posts/{slug}")
def read_post(session: SessionDep, slug: str) -> PostDetail:
    post = session.exec(select(Posts).where(Posts.slug == slug)).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    anime_detail = None
    season_detail = None

    if post.anime_id is not None:
        anime = session.exec(
            select(Animes)
            .where(Animes.anime_id == post.anime_id)
            .options(
                selectinload(Animes.age),  # type: ignore[arg-type]
                selectinload(Animes.genre),  # type: ignore[arg-type]
            )
        ).first()
        if not anime:
            raise HTTPException(status_code=404, detail="Anime not found")
        anime_slug, anime_name = anime.slug, anime.anime_name
        anime_detail = build_anime_detail(session, anime)
    else:
        season = session.exec(
            select(Seasons).where(Seasons.season_id == post.season_id)
        ).first()
        if not season:
            raise HTTPException(status_code=404, detail="Season not found")
        anime = session.exec(
            select(Animes)
            .where(Animes.anime_id == season.anime_id)
            .options(selectinload(Animes.genre))  # type: ignore[arg-type]
        ).first()
        if not anime:
            raise HTTPException(status_code=404, detail="Anime not found")
        anime_slug, anime_name = anime.slug, anime.anime_name
        season_detail = build_season_detail(session, season)

    tags = session.exec(
        select(Tags.name)
        .join(PostTags, col(PostTags.tag_id) == Tags.id)
        .where(PostTags.post_id == post.id)
    ).all()

    comments = session.exec(
        select(Comments)
        .where(Comments.post_id == post.id, Comments.status == CommentStatus.APPROVED)
        .order_by(col(Comments.created_at).asc())
    ).all()

    return PostDetail(
        slug=post.slug,
        title=post.title,
        backdrop_img=post.backdrop_img,
        status=post.status,
        sticky=post.sticky,
        views=post.views,
        last_updated=post.last_updated,
        tags=list(tags),
        anime_slug=anime_slug,
        anime_name=anime_name,
        genres=[g.genre_name for g in anime.genre],
        anime=anime_detail,
        season=season_detail,
        comments=[_comment_public(c) for c in comments],
    )


@router.get("/posts/{slug}/comments")
def list_comments(session: SessionDep, slug: str) -> list[CommentPublic]:
    post = session.exec(select(Posts).where(Posts.slug == slug)).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comments = session.exec(
        select(Comments)
        .where(Comments.post_id == post.id, Comments.status == CommentStatus.APPROVED)
        .order_by(col(Comments.created_at).asc())
    ).all()
    return [_comment_public(c) for c in comments]


@router.post("/posts/{slug}/comments", status_code=201)
def create_comment(
    session: SessionDep, slug: str, comment_in: CommentCreate
) -> CommentPublic:
    post = session.exec(select(Posts).where(Posts.slug == slug)).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if comment_in.parent_id is not None:
        parent = session.exec(
            select(Comments).where(
                Comments.id == comment_in.parent_id, Comments.post_id == post.id
            )
        ).first()
        if not parent:
            raise HTTPException(
                status_code=400, detail="parent_id does not belong to this post"
            )

    if any(domain in comment_in.author_email for domain in BLOCKED_EMAIL_DOMAINS):
        raise HTTPException(status_code=400, detail="Comment rejected")

    if CYRILLIC_RE.search(comment_in.body):
        raise HTTPException(status_code=400, detail="Comment rejected")

    duplicate = session.exec(
        select(Comments).where(
            Comments.post_id == post.id,
            Comments.author_name == comment_in.author_name,
            Comments.author_email == comment_in.author_email,
            Comments.body == comment_in.body,
        )
    ).first()
    if duplicate:
        return _comment_public(duplicate)

    status = (
        CommentStatus.PENDING
        if any(term in comment_in.body for term in SPAM_TERMS)
        else CommentStatus.APPROVED
    )

    comment = Comments(
        post_id=post.id,
        parent_id=comment_in.parent_id,
        author_name=comment_in.author_name,
        author_email=comment_in.author_email,
        author_url=comment_in.author_url,
        body=comment_in.body,
        created_at=datetime.now(UTC),
        status=status,
    )
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return _comment_public(comment)
