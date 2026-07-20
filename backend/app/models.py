# ruff: noqa: UP037
import datetime as dt
import decimal
import enum
import uuid
from datetime import UTC, datetime
from typing import Optional

from pydantic import EmailStr
from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKeyConstraint,
    Index,
    Numeric,
    PrimaryKeyConstraint,
    String,
    Table,
    Text,
    UniqueConstraint,
    text,
)
from sqlmodel import Field, Relationship, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(UTC)


class AuthorAccessScope(enum.StrEnum):
    ALL = "all"
    ONGOING = "ongoing"
    ACCESS_LIST = "access_list"


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    username: str | None = Field(default=None, unique=True, index=True, max_length=255)
    # None = no author/content-management access. Superusers implicitly have
    # full author access regardless of this field - see get_current_author.
    access_scope: AuthorAccessScope | None = Field(default=None)


# Properties to receive via API on creation. This is an admin-only,
# invite-based system (see users.py create_user) - password is optional here
# because the superuser doesn't set it; the account gets a random unusable
# password and the new author sets their own via the activation email link.
class UserCreate(UserBase):
    password: str | None = Field(default=None, min_length=8, max_length=128)


# Properties to receive via API on update, all are optional
class UserUpdate(SQLModel):
    email: EmailStr | None = Field(default=None, max_length=255)
    is_active: bool | None = None
    is_superuser: bool | None = None
    full_name: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    access_scope: AuthorAccessScope | None = Field(default=None)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    posts: list["Posts"] = Relationship(back_populates="author")


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


# --- GENERATED MODELS ---

class AnimesBackdropSource(enum.StrEnum):
    TMDB = 'tmdb'
    LOCAL = 'local'
    BUCKET = 'bucket'


class AnimesPosterSource(enum.StrEnum):
    TMDB = 'tmdb'
    LOCAL = 'local'
    URL = 'url'
    BUCKET = 'bucket'


class ContentContentType(enum.StrEnum):
    MOVIE = 'movie'
    PACK = 'pack'
    EPISODE = 'episode'
    # The Content row every tv-type Animes row is required to have
    # (content_id is NOT NULL) but that never itself gets links/comments/
    # view-tracking - downloads for a tv show live on its Episodes/Packs
    # content_id instead. Deliberately distinct from MOVIE so every check
    # that means "is this attachable" (PLAYABLE_TYPES, resolve_anime_id_for_
    # content, etc) excludes it automatically, without an extra lookup.
    TV = 'tv'


class SeasonsPosterSource(enum.StrEnum):
    TMDB = 'tmdb'
    LOCAL = 'local'
    BUCKET = 'bucket'


class SeasonStatus(enum.StrEnum):
    ONGOING = 'ongoing'
    COMPLETED = 'completed'


class AgeRatings(SQLModel, table=True):
    __tablename__ = 'age_ratings'
    __table_args__ = (
        PrimaryKeyConstraint('age_id', name='idx_17146_primary'),
    )

    age_id: int = Field(sa_column=Column('age_id', BigInteger, primary_key=True, autoincrement=True))
    age_name: str = Field(sa_column=Column('age_name', String(50), nullable=False))
    age_des: str = Field(sa_column=Column('age_des', String(50), nullable=False))

    animes: list["Animes"] = Relationship(back_populates='age')


class Genres(SQLModel, table=True):
    __table_args__ = (
        PrimaryKeyConstraint('genre_id', name='idx_17205_primary'),
        Index('idx_17205_genre_sid', 'genre_sid', unique=True)
    )

    genre_id: int = Field(sa_column=Column('genre_id', BigInteger, primary_key=True, autoincrement=True))
    genre_name: str = Field(sa_column=Column('genre_name', String(20), nullable=False))
    genre_sid: str = Field(sa_column=Column('genre_sid', String(20), nullable=False))

    anime: list["Animes"] = Relationship(back_populates='genre', sa_relationship_kwargs={'secondary': 'anime_genres'})


class Languages(SQLModel, table=True):
    __table_args__ = (
        PrimaryKeyConstraint('language_id', name='idx_17213_primary'),
        Index('idx_17213_language_sid', 'language_sid', unique=True)
    )

    language_id: int = Field(sa_column=Column('language_id', BigInteger, primary_key=True, autoincrement=True))
    language_sid: str = Field(sa_column=Column('language_sid', String(20), nullable=False))
    language_name: str = Field(sa_column=Column('language_name', String(20), nullable=False))

    season_dubs: list["SeasonDubs"] = Relationship(back_populates='language')


class OttPlatforms(SQLModel, table=True):
    __tablename__ = 'ott_platforms'
    __table_args__ = (
        PrimaryKeyConstraint('ott_id', name='idx_17255_primary'),
        Index('idx_17255_ott_sid', 'ott_sid', unique=True)
    )

    ott_id: int = Field(sa_column=Column('ott_id', BigInteger, primary_key=True, autoincrement=True))
    ott_sid: str = Field(sa_column=Column('ott_sid', String(20), nullable=False))
    ott_name: str = Field(sa_column=Column('ott_name', String(20), nullable=False))

    season_dubs: list["SeasonDubs"] = Relationship(back_populates='ott')


class Qualities(SQLModel, table=True):
    __table_args__ = (
        PrimaryKeyConstraint('quality_id', name='idx_17274_primary'),
    )

    quality_id: int = Field(sa_column=Column('quality_id', BigInteger, primary_key=True, autoincrement=True))
    quality_resolution: int = Field(sa_column=Column('quality_resolution', BigInteger, nullable=False))
    is_hevc: bool = Field(sa_column=Column('is_hevc', Boolean, nullable=False))
    is_hq: bool = Field(sa_column=Column('is_hq', Boolean, nullable=False))
    quality_order: int = Field(sa_column=Column('quality_order', BigInteger, nullable=False))
    quality_name: str = Field(sa_column=Column('quality_name', String(20), nullable=False))

    links: list["Links"] = Relationship(back_populates='quality')


class ServerInfo(SQLModel, table=True):
    __tablename__ = 'server_info'
    __table_args__ = (
        PrimaryKeyConstraint('server_id', name='idx_17309_primary'),
        Index('idx_17309_idx_server_sid', 'server_sid', unique=True)
    )

    server_id: int = Field(sa_column=Column('server_id', BigInteger, primary_key=True, autoincrement=True))
    server_sid: str = Field(sa_column=Column('server_sid', String(20), nullable=False))
    server_name: str = Field(sa_column=Column('server_name', String(30), nullable=False))
    server_order: int = Field(sa_column=Column('server_order', BigInteger, nullable=False))
    server_domain: str = Field(sa_column=Column('server_domain', String(50), nullable=False))
    api: str = Field(sa_column=Column('api', String(255), nullable=False))
    color: str = Field(sa_column=Column('color', String(10), nullable=False))
    is_enabled: bool = Field(sa_column=Column('is_enabled', Boolean, nullable=False, server_default=text('true')))
    # Upload-API domain (see app/uploaders/) - kept separate from
    # server_domain, which is the public download-resolution domain; these
    # file-host services often use a different domain for their upload API
    # than the one visitors download from, and both rotate independently.
    api_domain: str | None = Field(default=None, sa_column=Column('api_domain', String(100)))
    # Separate from is_enabled (which gates public visibility of already-
    # uploaded links) - this is the admin's start/stop switch for the
    # *background upload pipeline* specifically (app.link_upload), so
    # uploads to a server can be paused without hiding links that already
    # resolve fine there. Manual/instant admin-triggered uploads (see
    # app.api.routes.admin.upload_queue) bypass this switch on purpose.
    upload_enabled: bool = Field(
        sa_column=Column('upload_enabled', Boolean, nullable=False, server_default=text('true'))
    )

    link_servers: list["LinkServers"] = Relationship(back_populates='server', cascade_delete=True)


class Source(SQLModel, table=True):
    __table_args__ = (
        PrimaryKeyConstraint('source_id', name='idx_17323_primary'),
    )

    source_id: int = Field(sa_column=Column('source_id', BigInteger, primary_key=True, autoincrement=True))
    name: str = Field(sa_column=Column('name', String(20), nullable=False))
    domain: str = Field(sa_column=Column('domain', String(50), nullable=False))
    poster: str = Field(sa_column=Column('poster', String(10), nullable=False))
    poster_mid: str = Field(sa_column=Column('poster_mid', String(10), nullable=False))
    backdrop: str = Field(sa_column=Column('backdrop', String(10), nullable=False))
    poster_small: str = Field(sa_column=Column('poster_small', String(10), nullable=False))
    low: str = Field(sa_column=Column('low', String(10), nullable=False))
    backdrop_mid: str = Field(sa_column=Column('backdrop_mid', String(10), nullable=False))
    backdrop_high: str = Field(sa_column=Column('backdrop_high', String(10), nullable=False))


class Animes(SQLModel, table=True):
    __table_args__ = (
        ForeignKeyConstraint(['age_id'], ['age_ratings.age_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='age'),
        ForeignKeyConstraint(['content_id'], ['content.id'], ondelete='RESTRICT', onupdate='RESTRICT', name='animes_ibfk_2'),
        PrimaryKeyConstraint('anime_id', name='idx_17154_primary'),
        Index('idx_17154_age', 'age_id'),
        Index('idx_17154_anime_name', 'anime_name'),
        Index('idx_17154_content_id', 'content_id', unique=True),
        Index('idx_17154_slug', 'slug', unique=True),
        Index('idx_17154_slug_2', 'slug'),
        Index('idx_17154_slug_3', 'slug')
    )

    anime_id: int = Field(sa_column=Column('anime_id', BigInteger, primary_key=True, autoincrement=True))
    slug: str = Field(sa_column=Column('slug', String(255), nullable=False))
    anime_name: str = Field(sa_column=Column('anime_name', String(255), nullable=False))
    backdrop_source: AnimesBackdropSource = Field(sa_column=Column('backdrop_source', Enum(AnimesBackdropSource, values_callable=lambda cls: [member.value for member in cls], name='animes_backdrop_source'), nullable=False))
    backdrop_img: str = Field(sa_column=Column('backdrop_img', String(255), nullable=False))
    poster_source: AnimesPosterSource = Field(sa_column=Column('poster_source', Enum(AnimesPosterSource, values_callable=lambda cls: [member.value for member in cls], name='animes_poster_source'), nullable=False))
    poster_img: str = Field(sa_column=Column('poster_img', String(255), nullable=False))
    age_id: int = Field(sa_column=Column('age_id', BigInteger, nullable=False, server_default=text("'3'::bigint")))
    overview: str = Field(sa_column=Column('overview', Text, nullable=False))
    duration: int = Field(sa_column=Column('duration', BigInteger, nullable=False))
    rating: decimal.Decimal = Field(sa_column=Column('rating', Numeric(4, 2), nullable=False))
    type: str = Field(sa_column=Column('type', String(10), nullable=False))
    links_update: datetime = Field(default_factory=datetime.utcnow, sa_column=Column('links_update', DateTime(True), nullable=False))
    content_id: int = Field(sa_column=Column('content_id', BigInteger, nullable=False))
    anime_tmdb_id: int | None = Field(default=None, sa_column=Column('anime_tmdb_id', BigInteger))
    anime_rel_date: dt.date | None = Field(default=None, sa_column=Column('anime_rel_date', Date))

    age: AgeRatings = Relationship(back_populates='animes')
    # Content is created 1:1 alongside its Animes row and has no life of its
    # own - the FK just happens to live on this (the "child"/owning) side.
    # single_parent=True is required by SQLAlchemy to allow delete-orphan
    # cascade on this many-to-one/one-to-one direction (normally cascade
    # only flows from the referenced/"one" side); it also means a Content
    # row can never be repointed at a different Animes - correct, since
    # each Content row belongs to exactly the one row that created it.
    content: Content = Relationship(
        back_populates='animes', cascade_delete=True, sa_relationship_kwargs={'single_parent': True}
    )
    genre: list["Genres"] = Relationship(back_populates='anime', sa_relationship_kwargs={'secondary': 'anime_genres'})
    seasons: list["Seasons"] = Relationship(back_populates='anime', cascade_delete=True)
    post: Optional["Posts"] = Relationship(back_populates='anime', cascade_delete=True)  # noqa: UP045


class AuthorAnimeAccess(SQLModel, table=True):
    """Grants an access_list-scoped author permission to manage one anime
    (and everything under it - seasons, episodes, links, its post)."""

    __tablename__ = 'author_anime_access'

    user_id: uuid.UUID = Field(foreign_key='user.id', primary_key=True, ondelete='CASCADE')
    anime_id: int = Field(foreign_key='animes.anime_id', primary_key=True, ondelete='CASCADE')


class Links(SQLModel, table=True):
    __table_args__ = (
        ForeignKeyConstraint(['quality_id'], ['qualities.quality_id'], ondelete='SET NULL', onupdate='SET NULL', name='links_ibfk_1'),
        ForeignKeyConstraint(['content_id'], ['content.id'], ondelete='RESTRICT', onupdate='RESTRICT', name='links_ibfk_2'),
        PrimaryKeyConstraint('link_id', name='idx_17221_primary'),
        Index('idx_17221_gdriveid', 'gdriveid', unique=True),
        Index('idx_17221_idx_linksinfo_filter', 'is_live', 'type', 'link_id'),
        Index('idx_17221_quality', 'quality_id'),
        Index('ix_links_content_id', 'content_id')
    )

    link_id: int = Field(sa_column=Column('link_id', BigInteger, primary_key=True, autoincrement=True))
    filename: str = Field(sa_column=Column('filename', String(250), nullable=False))
    is_live: bool = Field(sa_column=Column('is_live', Boolean, nullable=False, server_default=text('true')))
    gdrive_email: str = Field(sa_column=Column('gdrive_email', String(90), nullable=False))
    gdriveid: str = Field(sa_column=Column('gdriveid', String(33), nullable=False))
    type: str = Field(sa_column=Column('type', String(10), nullable=False))
    mimetype: str = Field(sa_column=Column('mimetype', String(30), nullable=False))
    duration: int = Field(sa_column=Column('duration', BigInteger, nullable=False))
    note: str = Field(sa_column=Column('note', String(255), nullable=False))
    only_hindi: bool = Field(sa_column=Column('only_hindi', Boolean, nullable=False, server_default=text('false')))
    added_date: datetime = Field(sa_column=Column('added_date', DateTime(True), nullable=False, server_default=text('CURRENT_TIMESTAMP')))
    updated_date: datetime = Field(sa_column=Column('updated_date', DateTime(True), nullable=False, server_default=text('CURRENT_TIMESTAMP')))
    content_id: int = Field(sa_column=Column('content_id', BigInteger, nullable=False))
    size: decimal.Decimal | None = Field(default=None, sa_column=Column('size', Numeric))
    quality_id: int | None = Field(default=None, sa_column=Column('quality_id', BigInteger))

    quality: Qualities | None = Relationship(back_populates='links')
    link_servers: list["LinkServers"] = Relationship(back_populates='link', cascade_delete=True)
    content: Content = Relationship(back_populates="links")


t_anime_genres = Table(
    'anime_genres', SQLModel.metadata,
    Column('anime_id', BigInteger, primary_key=True),
    Column('genre_id', BigInteger, primary_key=True),
    ForeignKeyConstraint(['anime_id'], ['animes.anime_id'], ondelete='CASCADE', onupdate='CASCADE', name='anime_genres_ibfk_1'),
    ForeignKeyConstraint(['genre_id'], ['genres.genre_id'], ondelete='CASCADE', onupdate='CASCADE', name='anime_genres_ibfk_2'),
    PrimaryKeyConstraint('anime_id', 'genre_id', name='idx_17176_primary'),
    Index('idx_17176_genre_id', 'genre_id')
)


class LinkServerStatus(enum.StrEnum):
    PENDING = 'pending'
    SUCCESS = 'success'
    FAILED = 'failed'


class LinkServers(SQLModel, table=True):
    __tablename__ = 'link_servers'
    __table_args__ = (
        ForeignKeyConstraint(['link_id'], ['links.link_id'], ondelete='CASCADE', onupdate='CASCADE', name='link_servers_ibfk_2'),
        ForeignKeyConstraint(['server_id'], ['server_info.server_id'], ondelete='CASCADE', onupdate='CASCADE', name='link_servers_ibfk_1'),
        PrimaryKeyConstraint('ser_link_id', name='idx_17244_primary'),
        Index('idx_17244_idx_serverslinks_linkid_serverid_slug', 'link_id', 'server_id', 'slug'),
        Index('idx_17244_link_id', 'link_id', 'server_id', unique=True),
        Index('idx_17244_link_id_2', 'link_id'),
        Index('idx_17244_servers_links_ibfk_1', 'server_id')
    )

    ser_link_id: int = Field(sa_column=Column('ser_link_id', BigInteger, primary_key=True, autoincrement=True))
    link_id: int = Field(sa_column=Column('link_id', BigInteger, nullable=False))
    server_id: int = Field(sa_column=Column('server_id', BigInteger, nullable=False))
    slug: str | None = Field(default=None, sa_column=Column('slug', String(255)))
    # Upload job state - a row is created (status=pending) as soon as a link
    # is queued for a server, before any upload attempt, so retries/backoff
    # have somewhere to live. See app.link_upload.
    status: LinkServerStatus = Field(
        sa_column=Column(
            'status',
            Enum(LinkServerStatus, values_callable=lambda cls: [m.value for m in cls], name='link_server_status'),
            nullable=False,
            server_default=text("'pending'"),
        )
    )
    attempt_count: int = Field(sa_column=Column('attempt_count', BigInteger, nullable=False, server_default=text('0')))
    last_error: str | None = Field(default=None, sa_column=Column('last_error', String(500)))
    last_attempted_at: datetime | None = Field(
        default=None, sa_column=Column('last_attempted_at', DateTime(True))
    )
    next_attempt_at: datetime | None = Field(
        default=None, sa_column=Column('next_attempt_at', DateTime(True), index=True)
    )

    link: Links = Relationship(back_populates='link_servers')
    server: ServerInfo = Relationship(back_populates='link_servers')
    shortener_attempts: list["ShortenerAttempts"] = Relationship(
        back_populates='link_server', cascade_delete=True
    )
    download_events: list["DownloadEvents"] = Relationship(
        back_populates='link_server', cascade_delete=True
    )


class Seasons(SQLModel, table=True):
    __table_args__ = (
        ForeignKeyConstraint(['anime_id'], ['animes.anime_id'], ondelete='CASCADE', onupdate='CASCADE', name='seasons_ibfk_1'),
        PrimaryKeyConstraint('season_id', name='idx_17285_primary'),
        Index('idx_17285_anime_id', 'anime_id', 'season_number', unique=True)
    )

    season_id: int = Field(sa_column=Column('season_id', BigInteger, primary_key=True, autoincrement=True))
    anime_id: int = Field(sa_column=Column('anime_id', BigInteger, nullable=False))
    season_number: int = Field(sa_column=Column('season_number', BigInteger, nullable=False))
    season_name: str = Field(sa_column=Column('season_name', String(100), nullable=False))
    total_episodes: int = Field(sa_column=Column('total_episodes', BigInteger, nullable=False))
    season_overview: str = Field(sa_column=Column('season_overview', Text, nullable=False))
    poster_source: SeasonsPosterSource = Field(sa_column=Column('poster_source', Enum(SeasonsPosterSource, values_callable=lambda cls: [member.value for member in cls], name='seasons_poster_source'), nullable=False))
    rating: decimal.Decimal = Field(sa_column=Column('rating', Numeric(4, 2), nullable=False, server_default=text('0.00')))
    season_tmdb_id: str | None = Field(default=None, sa_column=Column('season_tmdb_id', String(20), server_default=text('NULL::character varying')))
    season_rel_date: dt.date | None = Field(default=None, sa_column=Column('season_rel_date', Date))
    poster_img: str | None = Field(default=None, sa_column=Column('poster_img', String(255), server_default=text('NULL::character varying')))
    status: SeasonStatus = Field(sa_column=Column('status', Enum(SeasonStatus, values_callable=lambda cls: [member.value for member in cls], name='season_status'), nullable=False, server_default=text("'ongoing'")))

    anime: Animes = Relationship(back_populates='seasons')
    episodes: list["Episodes"] = Relationship(back_populates='season', cascade_delete=True)
    packs: list["Packs"] = Relationship(back_populates='season', cascade_delete=True)
    post: Optional["Posts"] = Relationship(back_populates='season', cascade_delete=True)  # noqa: UP045
    dubs: list["SeasonDubs"] = Relationship(back_populates='season', cascade_delete=True)


class Episodes(SQLModel, table=True):
    __table_args__ = (
        ForeignKeyConstraint(['content_id'], ['content.id'], ondelete='RESTRICT', onupdate='RESTRICT', name='episodes_ibfk_2'),
        ForeignKeyConstraint(['season_id'], ['seasons.season_id'], ondelete='CASCADE', onupdate='CASCADE', name='episodes_ibfk_3'),
        PrimaryKeyConstraint('episode_id', name='idx_17189_primary'),
        Index('idx_17189_content_id', 'content_id', unique=True),
        Index('idx_17189_season_id', 'season_id', 'episode_number', unique=True)
    )

    episode_id: int = Field(sa_column=Column('episode_id', BigInteger, primary_key=True, autoincrement=True))
    season_id: int = Field(sa_column=Column('season_id', BigInteger, nullable=False))
    episode_number: int = Field(sa_column=Column('episode_number', BigInteger, nullable=False))
    content_id: int = Field(sa_column=Column('content_id', BigInteger, nullable=False))
    episode_tmdb_id: str | None = Field(default=None, sa_column=Column('episode_tmdb_id', String(20), server_default=text('NULL::character varying')))
    episode_name: str | None = Field(default=None, sa_column=Column('episode_name', String(150), server_default=text('NULL::character varying')))
    note: str | None = Field(default=None, sa_column=Column('note', String(255), server_default=text("''::character varying")))
    episode_runtime: int | None = Field(default=None, sa_column=Column('episode_runtime', BigInteger))
    episode_rating: decimal.Decimal | None = Field(default=None, sa_column=Column('episode_rating', Numeric(4, 2), server_default=text('NULL::numeric')))
    img: str | None = Field(default=None, sa_column=Column('img', String(255), server_default=text('NULL::character varying')))
    air_date: dt.date | None = Field(default=None, sa_column=Column('air_date', Date))
    overview: str | None = Field(default=None, sa_column=Column('overview', Text))

    # See Animes.content for why this is cascade_delete + single_parent
    # despite the FK living on this side.
    content: Content = Relationship(
        back_populates='episodes', cascade_delete=True, sa_relationship_kwargs={'single_parent': True}
    )
    season: Seasons = Relationship(back_populates='episodes')


class Packs(SQLModel, table=True):
    __table_args__ = (
        ForeignKeyConstraint(['content_id'], ['content.id'], ondelete='CASCADE', onupdate='CASCADE', name='packs_ibfk_2'),
        ForeignKeyConstraint(['season_id'], ['seasons.season_id'], ondelete='CASCADE', onupdate='CASCADE', name='packs_ibfk_1'),
        PrimaryKeyConstraint('pack_id', name='idx_17263_primary'),
        Index('idx_17263_content_id', 'content_id'),
        Index('idx_17263_my_season_id', 'season_id'),
        Index('ix_packs_season_id_start_ep_end_ep', 'season_id', 'start_ep', 'end_ep', unique=True)
    )

    pack_id: int = Field(sa_column=Column('pack_id', BigInteger, primary_key=True, autoincrement=True))
    season_id: int = Field(sa_column=Column('season_id', BigInteger, nullable=False))
    pack_name: str = Field(sa_column=Column('pack_name', String(100), nullable=False))
    start_ep: int = Field(sa_column=Column('start_ep', BigInteger, nullable=False))
    end_ep: int = Field(sa_column=Column('end_ep', BigInteger, nullable=False))
    content_id: int = Field(sa_column=Column('content_id', BigInteger, nullable=False))

    # See Animes.content for why this is cascade_delete + single_parent
    # despite the FK living on this side.
    content: Content = Relationship(
        back_populates='packs', cascade_delete=True, sa_relationship_kwargs={'single_parent': True}
    )
    season: Seasons = Relationship(back_populates='packs')


class Content(SQLModel, table=True):
    __table_args__ = (
        PrimaryKeyConstraint('id', name='idx_17182_primary'),
    )

    id: int = Field(sa_column=Column('id', BigInteger, primary_key=True, autoincrement=True))
    content_type: ContentContentType = Field(sa_column=Column('content_type', Enum(ContentContentType, values_callable=lambda cls: [member.value for member in cls], name='content_content_type'), nullable=False))
    respective_id: int | None = Field(default=None, sa_column=Column('respective_id', BigInteger))

    animes: Animes | None = Relationship(back_populates='content')
    episodes: Episodes | None = Relationship(back_populates='content')
    packs: Packs | None = Relationship(back_populates='content')
    # Normal-direction cascade (Content is genuinely the "one" side here,
    # Links the "many") - once a Content row is cascade-deleted via its
    # owning Animes/Episodes/Packs (see those models' `content` relationship),
    # every Link pointing at it goes too, instead of RESTRICT blocking the
    # Content delete.
    links: list["Links"] = Relationship(back_populates="content", cascade_delete=True)


class SeasonDubs(SQLModel, table=True):
    __tablename__ = 'season_dubs'
    __table_args__ = (
        ForeignKeyConstraint(['language_id'], ['languages.language_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='season_dubs_ibfk_2'),
        ForeignKeyConstraint(['ott_id'], ['ott_platforms.ott_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='season_dubs_ibfk_3'),
        ForeignKeyConstraint(['season_id'], ['seasons.season_id'], ondelete='CASCADE', onupdate='CASCADE', name='season_dubs_ibfk_1'),
        PrimaryKeyConstraint('season_id', 'ott_id', 'language_id', name='season_dubs_pkey'),
        Index('idx_17302_language_id', 'language_id'),
        Index('idx_17302_ott_id', 'ott_id'),
    )

    season_id: int = Field(sa_column=Column('season_id', BigInteger, primary_key=True))
    ott_id: int = Field(sa_column=Column('ott_id', BigInteger, primary_key=True))
    language_id: int = Field(sa_column=Column('language_id', BigInteger, primary_key=True))

    season: Seasons = Relationship(back_populates='dubs')
    ott: OttPlatforms = Relationship(back_populates='season_dubs')
    language: Languages = Relationship(back_populates='season_dubs')


# --- BLOG MIGRATION MODELS ---


class PostStatus(enum.StrEnum):
    ONGOING = "ongoing"
    COMPLETED = "completed"


class CommentStatus(enum.StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    SPAM = "spam"


class PostTags(SQLModel, table=True):
    __tablename__ = 'post_tags'

    post_id: int = Field(foreign_key='posts.id', primary_key=True, ondelete='CASCADE')
    tag_id: int = Field(foreign_key='tags.id', primary_key=True, ondelete='CASCADE')


class Tags(SQLModel, table=True):
    __tablename__ = 'tags'

    id: int | None = Field(default=None, primary_key=True)
    slug: str = Field(unique=True, max_length=50)
    name: str = Field(max_length=50)

    posts: list["Posts"] = Relationship(back_populates='tags', link_model=PostTags)


class Posts(SQLModel, table=True):
    __tablename__ = 'posts'
    __table_args__ = (
        CheckConstraint(
            '(anime_id IS NOT NULL) != (season_id IS NOT NULL)',
            name='posts_exactly_one_target',
        ),
        UniqueConstraint('anime_id', name='posts_anime_id_key'),
        UniqueConstraint('season_id', name='posts_season_id_key'),
    )

    id: int | None = Field(default=None, primary_key=True)
    anime_id: int | None = Field(default=None, foreign_key='animes.anime_id', ondelete='CASCADE')
    season_id: int | None = Field(default=None, foreign_key='seasons.season_id', ondelete='CASCADE')
    title: str = Field(max_length=255)
    slug: str = Field(unique=True, index=True, max_length=255)
    backdrop_img: str | None = Field(default=None, max_length=255)
    status: PostStatus
    sticky: bool = Field(default=False)
    views: int = Field(default=0)
    author_id: uuid.UUID | None = Field(default=None, foreign_key='user.id', ondelete='SET NULL')
    last_updated: datetime = Field(sa_type=DateTime(timezone=True))  # type: ignore

    anime: Animes | None = Relationship(back_populates='post')
    season: Seasons | None = Relationship(back_populates='post')
    author: User | None = Relationship(back_populates='posts')
    comments: list["Comments"] = Relationship(back_populates='post', cascade_delete=True)
    tags: list["Tags"] = Relationship(back_populates='posts', link_model=PostTags)


class Comments(SQLModel, table=True):
    __tablename__ = 'comments'

    id: int | None = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key='posts.id', ondelete='CASCADE')
    parent_id: int | None = Field(default=None, foreign_key='comments.id', ondelete='CASCADE')
    author_name: str = Field(max_length=50)
    author_email: str = Field(max_length=50)
    author_url: str | None = Field(default=None, max_length=255)
    body: str
    created_at: datetime = Field(
        default_factory=get_datetime_utc, sa_type=DateTime(timezone=True)  # type: ignore
    )
    status: CommentStatus = Field(default=CommentStatus.PENDING)

    post: Posts = Relationship(back_populates='comments')


class StreamComments(SQLModel, table=True):
    """
    Comments on player pages (movie/episode), keyed on content_id. Kept fully
    separate from Posts/Comments: download-page feedback (link slow, wrong
    quality) and streaming-page feedback (video lagging) are different
    audiences on different sites and shouldn't mix threads.
    """

    __tablename__ = 'stream_comments'

    id: int | None = Field(default=None, primary_key=True)
    content_id: int = Field(foreign_key='content.id', ondelete='CASCADE', index=True)
    parent_id: int | None = Field(
        default=None, foreign_key='stream_comments.id', ondelete='CASCADE'
    )
    author_name: str = Field(max_length=50)
    author_email: str = Field(max_length=50)
    author_url: str | None = Field(default=None, max_length=255)
    body: str
    created_at: datetime = Field(
        default_factory=get_datetime_utc, sa_type=DateTime(timezone=True)  # type: ignore
    )
    status: CommentStatus = Field(default=CommentStatus.PENDING)


# --- LINK SHORTENER / UNLOCK GATE MODELS ---


class LinkShorteners(SQLModel, table=True):
    __tablename__ = 'link_shorteners'

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=50)
    slug: str = Field(unique=True, max_length=50)
    api_url_template: str = Field(max_length=500)
    quick_url_template: str = Field(max_length=500)
    how_to_video_url: str | None = Field(default=None, max_length=500)
    message: str | None = Field(default=None, max_length=255)
    logo_url: str | None = Field(default=None, max_length=500)
    is_enabled: bool = Field(default=True)
    sort_order: int = Field(default=0)

    attempts: list["ShortenerAttempts"] = Relationship(
        back_populates='shortener', cascade_delete=True
    )


class UnlockConfig(SQLModel, table=True):
    __tablename__ = 'unlock_config'
    __table_args__ = (
        CheckConstraint('id = 1', name='unlock_config_singleton'),
    )

    id: int = Field(default=1, primary_key=True)
    required_solves: int = Field(default=4)
    report_threshold: int = Field(default=5)


class ShortenerAttempts(SQLModel, table=True):
    __tablename__ = 'shortener_attempts'

    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(unique=True, index=True, max_length=64)
    visitor_id: uuid.UUID = Field(index=True)
    shortener_id: int = Field(
        foreign_key='link_shorteners.id', ondelete='CASCADE', index=True
    )
    link_server_id: int = Field(
        foreign_key='link_servers.ser_link_id', ondelete='CASCADE', index=True
    )
    created_at: datetime = Field(
        default_factory=get_datetime_utc, sa_type=DateTime(timezone=True)  # type: ignore
    )
    solved_at: datetime | None = Field(
        default=None, sa_type=DateTime(timezone=True)  # type: ignore
    )
    reported_at: datetime | None = Field(
        default=None, sa_type=DateTime(timezone=True)  # type: ignore
    )
    report_reason: str | None = Field(default=None, max_length=255)

    shortener: LinkShorteners = Relationship(back_populates='attempts')
    link_server: LinkServers = Relationship(back_populates='shortener_attempts')


class DownloadEvents(SQLModel, table=True):
    __tablename__ = 'download_events'

    id: int | None = Field(default=None, primary_key=True)
    link_server_id: int = Field(
        foreign_key='link_servers.ser_link_id', ondelete='CASCADE', index=True
    )
    # Denormalized from link_servers -> links at write time (see
    # app.unlock.record_download_event) so the daily rollup never needs to
    # join back through links to know what was actually downloaded - same
    # reasoning as ContentViews storing content_id directly.
    content_id: int = Field(foreign_key='content.id', ondelete='CASCADE', index=True)
    visitor_id: uuid.UUID = Field(index=True)
    via_shortener_id: int | None = Field(
        default=None,
        foreign_key='link_shorteners.id',
        ondelete='SET NULL',
        index=True,
    )
    occurred_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
        index=True,
    )
    # Rolled into ContentDownloadDaily by the download-stats cron job, then
    # pruned - same raw-log-then-rollup pattern as ContentViews/rolled_up.
    rolled_up: bool = Field(default=False, index=True)

    link_server: LinkServers = Relationship(back_populates='download_events')
    via_shortener: LinkShorteners | None = Relationship()


# --- VIEW TRACKING / TRENDING MODELS ---


class ContentViews(SQLModel, table=True):
    """
    Raw dedup log: one row per (visitor, content, day). Only exists to make
    the same visitor watching the same episode twice in a day count once;
    once a row is rolled up it's only kept until the day is over, then
    pruned - it is not a permanent history.
    """

    __tablename__ = 'content_views'
    __table_args__ = (
        UniqueConstraint(
            'visitor_id', 'content_id', 'view_date',
            name='content_views_visitor_content_date_key',
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    visitor_id: uuid.UUID = Field(index=True)
    content_id: int = Field(foreign_key='content.id', ondelete='CASCADE', index=True)
    view_date: dt.date = Field(index=True)
    created_at: datetime = Field(
        default_factory=get_datetime_utc, sa_type=DateTime(timezone=True)  # type: ignore
    )
    rolled_up: bool = Field(default=False, index=True)


class ContentViewDaily(SQLModel, table=True):
    __tablename__ = 'content_view_daily'
    __table_args__ = (
        UniqueConstraint(
            'content_id', 'view_date', name='content_view_daily_content_date_key'
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    content_id: int = Field(foreign_key='content.id', ondelete='CASCADE', index=True)
    view_date: dt.date = Field(index=True)
    view_count: int = Field(default=0)


class SeasonViewDaily(SQLModel, table=True):
    __tablename__ = 'season_view_daily'
    __table_args__ = (
        UniqueConstraint(
            'season_id', 'view_date', name='season_view_daily_season_date_key'
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    season_id: int = Field(
        foreign_key='seasons.season_id', ondelete='CASCADE', index=True
    )
    view_date: dt.date = Field(index=True)
    view_count: int = Field(default=0)


class AnimeViewDaily(SQLModel, table=True):
    __tablename__ = 'anime_view_daily'
    __table_args__ = (
        UniqueConstraint(
            'anime_id', 'view_date', name='anime_view_daily_anime_date_key'
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    anime_id: int = Field(foreign_key='animes.anime_id', ondelete='CASCADE', index=True)
    view_date: dt.date = Field(index=True)
    view_count: int = Field(default=0)


# Monthly tier for the same daily tables above - a *ViewDaily row older than
# app.trending.DAILY_RETENTION_DAYS gets folded into the matching *ViewMonthly
# row and deleted, same "day 1..30, then month 3/month 2/month 1" tiering as
# the download-stats tables below.


class ContentViewMonthly(SQLModel, table=True):
    __tablename__ = 'content_view_monthly'
    __table_args__ = (
        UniqueConstraint(
            'content_id', 'year', 'month', name='content_view_monthly_content_ym_key'
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    content_id: int = Field(foreign_key='content.id', ondelete='CASCADE', index=True)
    year: int = Field(index=True)
    month: int
    view_count: int = Field(default=0)


class SeasonViewMonthly(SQLModel, table=True):
    __tablename__ = 'season_view_monthly'
    __table_args__ = (
        UniqueConstraint(
            'season_id', 'year', 'month', name='season_view_monthly_season_ym_key'
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    season_id: int = Field(foreign_key='seasons.season_id', ondelete='CASCADE', index=True)
    year: int = Field(index=True)
    month: int
    view_count: int = Field(default=0)


class AnimeViewMonthly(SQLModel, table=True):
    __tablename__ = 'anime_view_monthly'
    __table_args__ = (
        UniqueConstraint(
            'anime_id', 'year', 'month', name='anime_view_monthly_anime_ym_key'
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    anime_id: int = Field(foreign_key='animes.anime_id', ondelete='CASCADE', index=True)
    year: int = Field(index=True)
    month: int
    view_count: int = Field(default=0)


# --- DOWNLOAD STATS MODELS ---
# Content is high-cardinality (tens of thousands of movies/episodes/packs) so
# it gets the same two-tier treatment as views: a daily table kept for a
# rolling ~30 days, compacted into a monthly table (and deleted) once older
# than that. Servers and shorteners are tiny in number (4-10 each) so they
# skip the monthly tier entirely and are just incremented inline at write
# time - no batching, no dedup, the row count is negligible forever.


class ContentDownloadDaily(SQLModel, table=True):
    __tablename__ = 'content_download_daily'
    __table_args__ = (
        UniqueConstraint(
            'content_id', 'download_date', name='content_download_daily_content_date_key'
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    content_id: int = Field(foreign_key='content.id', ondelete='CASCADE', index=True)
    download_date: dt.date = Field(index=True)
    download_count: int = Field(default=0)


class ContentDownloadMonthly(SQLModel, table=True):
    __tablename__ = 'content_download_monthly'
    __table_args__ = (
        UniqueConstraint(
            'content_id', 'year', 'month', name='content_download_monthly_content_ym_key'
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    content_id: int = Field(foreign_key='content.id', ondelete='CASCADE', index=True)
    year: int = Field(index=True)
    month: int
    download_count: int = Field(default=0)


class ServerDownloadDaily(SQLModel, table=True):
    __tablename__ = 'server_download_daily'
    __table_args__ = (
        UniqueConstraint(
            'server_id', 'download_date', name='server_download_daily_server_date_key'
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    server_id: int = Field(foreign_key='server_info.server_id', ondelete='CASCADE', index=True)
    download_date: dt.date = Field(index=True)
    download_count: int = Field(default=0)


class ShortenerFunnelDaily(SQLModel, table=True):
    __tablename__ = 'shortener_funnel_daily'
    __table_args__ = (
        UniqueConstraint(
            'shortener_id', 'stat_date', name='shortener_funnel_daily_shortener_date_key'
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    shortener_id: int = Field(
        foreign_key='link_shorteners.id', ondelete='CASCADE', index=True
    )
    stat_date: dt.date = Field(index=True)
    attempts: int = Field(default=0)
    solved: int = Field(default=0)
    reported: int = Field(default=0)
