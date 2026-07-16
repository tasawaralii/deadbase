from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import ColumnElement
from sqlalchemy.orm import selectinload
from sqlmodel import col, func, select

from app.api.deps import SessionDep
from app.media import build_download_links, get_watch_servers, resolve_image_urls
from app.models import Animes, Episodes, Genres, Packs, Seasons
from app.schemas.anime import AnimeDetail, AnimeListPublic, AnimeSummary
from app.schemas.season import SeasonSummary

router = APIRouter()


@router.get("/anime")
def list_anime(
    session: SessionDep,
    q: str | None = None,
    genre: str | None = None,
    anime_type: str | None = Query(None, alias="type"),
    sort: Literal["rating", "latest", "name"] = "latest",
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> AnimeListPublic:
    conditions: list[ColumnElement[bool]] = []
    if q:
        conditions.append(col(Animes.anime_name).ilike(f"%{q}%"))
    if anime_type:
        conditions.append(col(Animes.type) == anime_type)
    if genre:
        conditions.append(Animes.genre.any(Genres.genre_sid == genre))  # type: ignore[attr-defined]

    total = session.exec(
        select(func.count()).select_from(Animes).where(*conditions)
    ).one()

    order = {
        "rating": col(Animes.rating).desc(),
        "latest": col(Animes.anime_rel_date).desc().nullslast(),
        "name": col(Animes.anime_name).asc(),
    }[sort]

    season_count_subq = (
        select(func.count(col(Seasons.season_id)))
        .where(Seasons.anime_id == Animes.anime_id)
        .scalar_subquery()
    )

    rows = session.exec(
        select(Animes, season_count_subq)
        .where(*conditions)
        .options(
            selectinload(Animes.age),  # type: ignore[arg-type]
            selectinload(Animes.genre),  # type: ignore[arg-type]
        )
        .order_by(order)  # type: ignore[arg-type]
        .offset((page - 1) * limit)
        .limit(limit)
    ).all()

    data = [
        AnimeSummary(
            slug=anime.slug,
            anime_name=anime.anime_name,
            type=anime.type,
            poster=resolve_image_urls(anime.poster_source, anime.poster_img, "poster"),
            rating=anime.rating,
            age_rating=anime.age.age_name,
            genres=[g.genre_name for g in anime.genre],
            season_count=season_count if anime.type == "tv" else None,
        )
        for anime, season_count in rows
    ]

    return AnimeListPublic(data=data, page=page, limit=limit, count=total)


@router.get("/anime/{slug}")
def read_anime(session: SessionDep, slug: str) -> AnimeDetail:
    anime = session.exec(
        select(Animes)
        .where(Animes.slug == slug)
        .options(
            selectinload(Animes.age),  # type: ignore[arg-type]
            selectinload(Animes.genre),  # type: ignore[arg-type]
        )
    ).first()
    if not anime:
        raise HTTPException(status_code=404, detail="Anime not found")

    base = {
        "slug": anime.slug,
        "anime_name": anime.anime_name,
        "type": anime.type,
        "poster": resolve_image_urls(anime.poster_source, anime.poster_img, "poster"),
        "backdrop": resolve_image_urls(
            anime.backdrop_source, anime.backdrop_img, "backdrop"
        ),
        "overview": anime.overview,
        "duration": anime.duration,
        "rating": anime.rating,
        "age_rating": anime.age.age_name,
        "genres": [g.genre_name for g in anime.genre],
        "release_date": anime.anime_rel_date,
    }

    if anime.type == "movie":
        return AnimeDetail(
            **base,
            links=build_download_links(session, anime.content_id),
            watch_servers=get_watch_servers(),
        )

    episode_count_subq = (
        select(func.count(col(Episodes.episode_id)))
        .where(Episodes.season_id == Seasons.season_id)
        .scalar_subquery()
    )
    pack_count_subq = (
        select(func.count(col(Packs.pack_id)))
        .where(Packs.season_id == Seasons.season_id)
        .scalar_subquery()
    )

    seasons = session.exec(
        select(Seasons, episode_count_subq, pack_count_subq)
        .where(Seasons.anime_id == anime.anime_id)
        .order_by(col(Seasons.season_number).asc())
    ).all()

    return AnimeDetail(
        **base,
        seasons=[
            SeasonSummary(
                season_number=season.season_number,
                season_name=season.season_name,
                poster=resolve_image_urls(
                    season.poster_source, season.poster_img, "poster"
                ),
                rating=season.rating,
                episode_count=episode_count,
                pack_count=pack_count,
            )
            for season, episode_count, pack_count in seasons
        ],
    )
