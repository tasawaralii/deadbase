from sqlmodel import SQLModel


class StatsOverview(SQLModel):
    anime_count: int
    season_count: int
    episode_count: int
    pack_count: int
    link_count: int
    author_count: int
    pending_comments: int
    pending_stream_comments: int


class ShortenerFunnelStats(SQLModel):
    shortener_id: int
    name: str
    is_enabled: bool
    attempts: int
    solved: int
    reported: int


class ServerPerformanceStats(SQLModel):
    server_id: int
    server_name: str
    is_enabled: bool
    downloads: int


class UnlockFunnelStats(SQLModel):
    shorteners: list[ShortenerFunnelStats]
    servers: list[ServerPerformanceStats]


class ContentDownloadItem(SQLModel):
    content_id: int
    content_type: str
    title: str
    downloads: int


class ContentDownloadList(SQLModel):
    data: list[ContentDownloadItem]
