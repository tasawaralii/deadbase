import uuid
from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import TokenPayload, User

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        # This is an auth failure (a stale token no longer resolving to a
        # real account), not a REST "resource not found" - the frontend's
        # global error handler treats 401/403 as "log out and redirect to
        # /login", which is exactly what should happen here.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


def get_current_author(current_user: CurrentUser) -> User:
    # Superusers can do everything an author can, on top of config access.
    if not current_user.is_superuser and current_user.access_scope is None:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


CurrentAuthor = Annotated[User, Depends(get_current_author)]


VISITOR_COOKIE_NAME = "visitor_id"
VISITOR_COOKIE_MAX_AGE = 60 * 60 * 24 * 365


def get_visitor_id(request: Request, response: Response) -> uuid.UUID:
    raw = request.cookies.get(VISITOR_COOKIE_NAME)
    if raw:
        try:
            return uuid.UUID(raw)
        except ValueError:
            pass

    visitor_id = uuid.uuid4()
    response.set_cookie(
        VISITOR_COOKIE_NAME,
        str(visitor_id),
        max_age=VISITOR_COOKIE_MAX_AGE,
        httponly=True,
        secure=settings.ENVIRONMENT != "local",
        samesite="lax",
    )
    return visitor_id


VisitorId = Annotated[uuid.UUID, Depends(get_visitor_id)]
