from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, select

from app.api.deps import CurrentAuthor, SessionDep, get_current_author
from app.models import Posts, Seasons, Tags
from app.permissions import require_anime_write_access
from app.schemas.admin_post import PostAdminPublic, PostUpdate
from app.schemas.common import TagPublic

router = APIRouter(
    prefix="/posts", tags=["author"], dependencies=[Depends(get_current_author)]
)


def _to_public(post: Posts) -> PostAdminPublic:
    return PostAdminPublic(
        id=post.id,
        anime_id=post.anime_id,
        season_id=post.season_id,
        title=post.title,
        slug=post.slug,
        backdrop_img=post.backdrop_img,
        status=post.status,
        sticky=post.sticky,
        views=post.views,
        last_updated=post.last_updated,
        tags=[TagPublic(name=t.name, slug=t.slug) for t in post.tags],
    )


def _get_post_with_access(session: SessionDep, author: CurrentAuthor, post_id: int) -> Posts:
    post = session.get(Posts, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.anime_id is not None:
        require_anime_write_access(session, author, post.anime_id)
    else:
        season = session.get(Seasons, post.season_id)
        if season is None:
            raise HTTPException(status_code=404, detail="Season not found")
        require_anime_write_access(session, author, season.anime_id, season=season)

    return post


@router.get("/{post_id}")
def get_post(session: SessionDep, author: CurrentAuthor, post_id: int) -> PostAdminPublic:
    post = _get_post_with_access(session, author, post_id)
    return _to_public(post)


@router.patch("/{post_id}")
def update_post(
    session: SessionDep, author: CurrentAuthor, post_id: int, body: PostUpdate
) -> PostAdminPublic:
    post = _get_post_with_access(session, author, post_id)

    updates = body.model_dump(exclude_unset=True)

    if "tag_ids" in updates:
        tag_ids = updates.pop("tag_ids")
        tags: list[Tags] = []
        if tag_ids:
            tags = list(session.exec(select(Tags).where(col(Tags.id).in_(tag_ids))))
            found_ids = {t.id for t in tags}
            missing_ids = set(tag_ids) - found_ids
            if missing_ids:
                raise HTTPException(
                    status_code=400,
                    detail=f"No tag with id(s): {', '.join(str(i) for i in sorted(missing_ids))}",
                )
        post.tags = tags

    for field, value in updates.items():
        setattr(post, field, value)

    session.add(post)
    session.commit()
    session.refresh(post)
    return _to_public(post)
