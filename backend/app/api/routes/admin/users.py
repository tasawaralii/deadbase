import logging
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, delete, func, select

from app import crud
from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.core.config import settings
from app.models import (
    Animes,
    AuthorAnimeAccess,
    Item,
    Message,
    User,
    UserCreate,
    UserPublic,
    UsersPublic,
    UserUpdate,
)
from app.schemas.admin_user import AnimeAccessGrantPublic, AnimeAccessListPublic
from app.utils import (
    generate_new_account_email,
    generate_password_reset_token,
    send_email,
)

logger = logging.getLogger(__name__)

# User account administration (create/list/update/delete other users, grant/
# revoke per-anime access) - superuser-only config, distinct from /me
# (self-service for any authenticated user) and /author (content CRUD).
router = APIRouter(
    prefix="/users", tags=["admin"], dependencies=[Depends(get_current_active_superuser)]
)


@router.get("/", response_model=UsersPublic)
def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """
    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()

    statement = (
        select(User).order_by(col(User.created_at).desc()).offset(skip).limit(limit)
    )
    users = session.exec(statement).all()

    users_public = [UserPublic.model_validate(user) for user in users]
    return UsersPublic(data=users_public, count=count)


@router.post("/", response_model=UserPublic)
def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    """
    Create new user.
    """
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    user = crud.create_user(session=session, user_create=user_in)

    # Invite-only account creation: the author sets their own password via
    # this link rather than the superuser choosing one for them.
    token = generate_password_reset_token(email=user_in.email)
    if settings.emails_enabled:
        email_data = generate_new_account_email(
            email_to=user_in.email, username=user_in.email, token=token
        )
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    else:
        link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
        logger.warning(
            "Email sending is disabled - activation link for %s: %s",
            user_in.email,
            link,
        )
    return user


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(user_id: uuid.UUID, session: SessionDep) -> Any:
    """
    Get a specific user by id.
    """
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserPublic)
def update_user(*, session: SessionDep, user_id: uuid.UUID, user_in: UserUpdate) -> Any:
    """
    Update a user.
    """
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )

    db_user = crud.update_user(session=session, db_user=db_user, user_in=user_in)
    return db_user


@router.delete("/{user_id}")
def delete_user(session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID) -> Message:
    """
    Delete a user.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    statement = delete(Item).where(col(Item.owner_id) == user_id)
    session.exec(statement)
    session.delete(user)
    session.commit()
    return Message(message="User deleted successfully")


def _get_user(session: SessionDep, user_id: uuid.UUID) -> User:
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}/anime-access/")
def list_anime_access(session: SessionDep, user_id: uuid.UUID) -> AnimeAccessListPublic:
    user = _get_user(session, user_id)

    animes = session.exec(
        select(Animes)
        .join(AuthorAnimeAccess, col(AuthorAnimeAccess.anime_id) == col(Animes.anime_id))
        .where(AuthorAnimeAccess.user_id == user.id)
        .order_by(col(Animes.anime_name))
    ).all()

    return AnimeAccessListPublic(
        data=[
            AnimeAccessGrantPublic(
                anime_id=a.anime_id, slug=a.slug, anime_name=a.anime_name, type=a.type
            )
            for a in animes
        ]
    )


@router.post("/{user_id}/anime-access/{anime_id}", status_code=201)
def grant_anime_access(
    session: SessionDep, user_id: uuid.UUID, anime_id: int
) -> AnimeAccessGrantPublic:
    user = _get_user(session, user_id)

    anime = session.get(Animes, anime_id)
    if anime is None:
        raise HTTPException(status_code=404, detail="Anime not found")

    existing = session.exec(
        select(AuthorAnimeAccess).where(
            AuthorAnimeAccess.user_id == user.id,
            AuthorAnimeAccess.anime_id == anime_id,
        )
    ).first()
    if existing is None:
        session.add(AuthorAnimeAccess(user_id=user.id, anime_id=anime_id))
        session.commit()

    return AnimeAccessGrantPublic(
        anime_id=anime.anime_id, slug=anime.slug, anime_name=anime.anime_name, type=anime.type
    )


@router.delete("/{user_id}/anime-access/{anime_id}", status_code=204)
def revoke_anime_access(session: SessionDep, user_id: uuid.UUID, anime_id: int) -> None:
    user = _get_user(session, user_id)

    grant = session.exec(
        select(AuthorAnimeAccess).where(
            AuthorAnimeAccess.user_id == user.id,
            AuthorAnimeAccess.anime_id == anime_id,
        )
    ).first()
    if grant is None:
        raise HTTPException(status_code=404, detail="This anime is not granted to this user")

    session.delete(grant)
    session.commit()
