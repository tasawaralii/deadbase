# ruff: noqa: UP037
import datetime as dt
import decimal
import enum
import uuid
from datetime import UTC, datetime

from pydantic import EmailStr
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Numeric,
    PrimaryKeyConstraint,
    String,
    Table,
    Text,
    text,
)
from sqlmodel import Field, Relationship, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(UTC)


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(SQLModel):
    email: EmailStr | None = Field(default=None, max_length=255)
    is_active: bool | None = None
    is_superuser: bool | None = None
    full_name: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)


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


class AnimesPosterSource(enum.StrEnum):
    TMDB = 'tmdb'
    LOCAL = 'local'
    URL = 'url'


class ContentContentType(enum.StrEnum):
    MOVIE = 'movie'
    PACK = 'pack'
    EPISODE = 'episode'


class SeasonsPosterSource(enum.StrEnum):
    TMDB = 'tmdb'
    LOCAL = 'local'


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


class OttPlatforms(SQLModel, table=True):
    __tablename__ = 'ott_platforms'
    __table_args__ = (
        PrimaryKeyConstraint('ott_id', name='idx_17255_primary'),
        Index('idx_17255_ott_sid', 'ott_sid', unique=True)
    )

    ott_id: int = Field(sa_column=Column('ott_id', BigInteger, primary_key=True, autoincrement=True))
    ott_sid: str = Field(sa_column=Column('ott_sid', String(20), nullable=False))
    ott_name: str = Field(sa_column=Column('ott_name', String(20), nullable=False))


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

    link_servers: list["LinkServers"] = Relationship(back_populates='server')


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
    content: Content = Relationship(back_populates='animes')
    genre: list["Genres"] = Relationship(back_populates='anime', sa_relationship_kwargs={'secondary': 'anime_genres'})
    seasons: list["Seasons"] = Relationship(back_populates='anime')


class Links(SQLModel, table=True):
    __table_args__ = (
        ForeignKeyConstraint(['quality_id'], ['qualities.quality_id'], ondelete='SET NULL', onupdate='SET NULL', name='links_ibfk_1'),
        PrimaryKeyConstraint('link_id', name='idx_17221_primary'),
        Index('idx_17221_gdriveid', 'gdriveid', unique=True),
        Index('idx_17221_idx_linksinfo_filter', 'is_live', 'type', 'link_id'),
        Index('idx_17221_quality', 'quality_id')
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
    content_id: int = Field(sa_column=Column('content_id', BigInteger, ForeignKey("content.id"), nullable=False))
    size: decimal.Decimal | None = Field(default=None, sa_column=Column('size', Numeric))
    quality_id: int | None = Field(default=None, sa_column=Column('quality_id', BigInteger))

    quality: Qualities | None = Relationship(back_populates='links')
    link_servers: list["LinkServers"] = Relationship(back_populates='link')
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
    is_uploaded: int = Field(sa_column=Column('is_uploaded', BigInteger, nullable=False, server_default=text("'0'::bigint")))
    slug: str = Field(sa_column=Column('slug', String(255), nullable=False))

    link: Links = Relationship(back_populates='link_servers')
    server: ServerInfo = Relationship(back_populates='link_servers')


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

    anime: Animes = Relationship(back_populates='seasons')
    episodes: list["Episodes"] = Relationship(back_populates='season')
    packs: list["Packs"] = Relationship(back_populates='season')


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

    content: Content = Relationship(back_populates='episodes')
    season: Seasons = Relationship(back_populates='episodes')


class Packs(SQLModel, table=True):
    __table_args__ = (
        ForeignKeyConstraint(['content_id'], ['content.id'], ondelete='CASCADE', onupdate='CASCADE', name='packs_ibfk_2'),
        ForeignKeyConstraint(['season_id'], ['seasons.season_id'], ondelete='CASCADE', onupdate='CASCADE', name='packs_ibfk_1'),
        PrimaryKeyConstraint('pack_id', name='idx_17263_primary'),
        Index('idx_17263_content_id', 'content_id'),
        Index('idx_17263_my_season_id', 'season_id')
    )

    pack_id: int = Field(sa_column=Column('pack_id', BigInteger, primary_key=True, autoincrement=True))
    season_id: int = Field(sa_column=Column('season_id', BigInteger, nullable=False))
    pack_name: str = Field(sa_column=Column('pack_name', String(100), nullable=False))
    start_ep: int = Field(sa_column=Column('start_ep', BigInteger, nullable=False))
    end_ep: int = Field(sa_column=Column('end_ep', BigInteger, nullable=False))
    content_id: int = Field(sa_column=Column('content_id', BigInteger, nullable=False))

    content: Content = Relationship(back_populates='packs')
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
    links: list["Links"] = Relationship(back_populates="content")


t_season_dubs = Table(
    'season_dubs', SQLModel.metadata,
    Column('season_id', BigInteger, nullable=False),
    Column('ott_id', BigInteger, nullable=False),
    Column('language_id', BigInteger, nullable=False),
    ForeignKeyConstraint(['language_id'], ['languages.language_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='season_dubs_ibfk_2'),
    ForeignKeyConstraint(['ott_id'], ['ott_platforms.ott_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='season_dubs_ibfk_3'),
    ForeignKeyConstraint(['season_id'], ['seasons.season_id'], ondelete='CASCADE', onupdate='CASCADE', name='season_dubs_ibfk_1'),
    Index('idx_17302_language_id', 'language_id'),
    Index('idx_17302_ott_id', 'ott_id'),
    Index('idx_17302_season_id', 'season_id', 'ott_id', 'language_id', unique=True)
)
