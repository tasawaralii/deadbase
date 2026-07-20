from sqlmodel import SQLModel


class ServerCreate(SQLModel):
    server_sid: str
    server_name: str
    server_order: int = 0
    server_domain: str
    api: str
    color: str
    is_enabled: bool = True


class ServerUpdate(SQLModel):
    server_sid: str | None = None
    server_name: str | None = None
    server_order: int | None = None
    server_domain: str | None = None
    api: str | None = None
    color: str | None = None
    is_enabled: bool | None = None


class ServerAdminPublic(SQLModel):
    server_id: int
    server_sid: str
    server_name: str
    server_order: int
    server_domain: str
    api: str
    color: str
    is_enabled: bool


class ServerAdminListPublic(SQLModel):
    data: list[ServerAdminPublic]
