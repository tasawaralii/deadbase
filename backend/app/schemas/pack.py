from sqlmodel import SQLModel

from app.schemas.common import DownloadLink, LinkPublic


class PackSummary(SQLModel):
    pack_name: str
    start_ep: int
    end_ep: int
    link_count: int


class PackDetail(SQLModel):
    pack_name: str
    start_ep: int
    end_ep: int
    links: list[LinkPublic]
    watch_servers: list[DownloadLink]
