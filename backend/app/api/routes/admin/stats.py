from fastapi import APIRouter, Depends, Query
from sqlmodel import col, func, select

from app.api.deps import SessionDep, get_current_active_superuser
from app.download_stats import (
    get_server_downloads,
    get_shortener_funnel,
    get_top_content_downloads,
)
from app.models import (
    Animes,
    Comments,
    CommentStatus,
    Content,
    ContentContentType,
    Episodes,
    Links,
    LinkShorteners,
    Packs,
    Seasons,
    ServerInfo,
    StreamComments,
    User,
)
from app.schemas.admin_stats import (
    ContentDownloadItem,
    ContentDownloadList,
    ServerPerformanceStats,
    ShortenerFunnelStats,
    StatsOverview,
    UnlockFunnelStats,
)
from app.schemas.trending import TrendingAnimeList
from app.trending import TrendingWindow, build_trending_anime_list

router = APIRouter(
    prefix="/stats", tags=["admin"], dependencies=[Depends(get_current_active_superuser)]
)


@router.get("/overview")
def stats_overview(session: SessionDep) -> StatsOverview:
    def count_of(model: type) -> int:
        return session.exec(select(func.count()).select_from(model)).one()

    author_count = session.exec(
        select(func.count()).select_from(User).where(col(User.access_scope).is_not(None))
    ).one()
    pending_comments = session.exec(
        select(func.count())
        .select_from(Comments)
        .where(Comments.status == CommentStatus.PENDING)
    ).one()
    pending_stream_comments = session.exec(
        select(func.count())
        .select_from(StreamComments)
        .where(StreamComments.status == CommentStatus.PENDING)
    ).one()

    return StatsOverview(
        anime_count=count_of(Animes),
        season_count=count_of(Seasons),
        episode_count=count_of(Episodes),
        pack_count=count_of(Packs),
        link_count=count_of(Links),
        author_count=author_count,
        pending_comments=pending_comments,
        pending_stream_comments=pending_stream_comments,
    )


@router.get("/unlock-funnel")
def stats_unlock_funnel(
    session: SessionDep, window: TrendingWindow = Query("all")
) -> UnlockFunnelStats:
    shorteners = {
        s.id: s
        for s in session.exec(
            select(LinkShorteners).order_by(col(LinkShorteners.sort_order).asc())
        ).all()
    }
    funnel_rows = get_shortener_funnel(session, window)
    shortener_stats = [
        ShortenerFunnelStats(
            shortener_id=shortener_id,
            name=shorteners[shortener_id].name,
            is_enabled=shorteners[shortener_id].is_enabled,
            attempts=attempts,
            solved=solved,
            reported=reported,
        )
        for shortener_id, attempts, solved, reported in funnel_rows
        if shortener_id in shorteners
    ]

    servers = {
        s.server_id: s
        for s in session.exec(
            select(ServerInfo).order_by(col(ServerInfo.server_order).asc())
        ).all()
    }
    download_rows = get_server_downloads(session, window)
    server_stats = [
        ServerPerformanceStats(
            server_id=server_id,
            server_name=servers[server_id].server_name,
            is_enabled=servers[server_id].is_enabled,
            downloads=downloads,
        )
        for server_id, downloads in download_rows
        if server_id in servers
    ]

    return UnlockFunnelStats(shorteners=shortener_stats, servers=server_stats)


def _content_label(session: SessionDep, content_id: int) -> tuple[str, str] | None:
    """Returns (content_type, human title) for a content_id, or None if unresolvable."""
    content = session.get(Content, content_id)
    if content is None:
        return None

    if content.content_type == ContentContentType.MOVIE:
        anime = session.get(Animes, content.respective_id)
        return ("movie", anime.anime_name) if anime else None

    if content.content_type == ContentContentType.EPISODE:
        episode = session.get(Episodes, content.respective_id)
        season = session.get(Seasons, episode.season_id) if episode else None
        anime = session.get(Animes, season.anime_id) if season else None
        if not (episode and season and anime):
            return None
        title = f"{anime.anime_name} S{season.season_number:02d}E{episode.episode_number:02d}"
        return ("episode", title)

    if content.content_type == ContentContentType.PACK:
        pack = session.get(Packs, content.respective_id)
        season = session.get(Seasons, pack.season_id) if pack else None
        anime = session.get(Animes, season.anime_id) if season else None
        if not (pack and season and anime):
            return None
        title = f"{anime.anime_name} S{season.season_number:02d} Pack {pack.start_ep}-{pack.end_ep}"
        return ("pack", title)

    return None


@router.get("/content-downloads")
def stats_content_downloads(
    session: SessionDep,
    window: TrendingWindow = Query("today"),
    limit: int = Query(20, ge=1, le=50),
) -> ContentDownloadList:
    rows = get_top_content_downloads(session, window, limit)

    data = []
    for content_id, downloads in rows:
        label = _content_label(session, content_id)
        if label is None:
            continue
        content_type, title = label
        data.append(
            ContentDownloadItem(
                content_id=content_id,
                content_type=content_type,
                title=title,
                downloads=downloads,
            )
        )
    return ContentDownloadList(data=data)


@router.get("/views")
def stats_views(
    session: SessionDep,
    window: TrendingWindow = Query("today"),
    limit: int = Query(20, ge=1, le=50),
) -> TrendingAnimeList:
    return build_trending_anime_list(session, window, limit)
