from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, select

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import ServerInfo
from app.schemas.admin_server import (
    ServerAdminListPublic,
    ServerAdminPublic,
    ServerCreate,
    ServerUpdate,
)

# Deleting a server cascades to every LinkServers row that uses it (see
# ServerInfo.link_servers, cascade_delete=True) - i.e. every link's presence
# on that server across the whole site. Disabling (is_enabled=False) is the
# safer lever for "stop using this server" - delete is for real cleanup of a
# server that's genuinely gone.
router = APIRouter(
    prefix="/servers", tags=["admin"], dependencies=[Depends(get_current_active_superuser)]
)


def _to_public(server: ServerInfo) -> ServerAdminPublic:
    return ServerAdminPublic(
        server_id=server.server_id,
        server_sid=server.server_sid,
        server_name=server.server_name,
        server_order=server.server_order,
        server_domain=server.server_domain,
        api=server.api,
        color=server.color,
        is_enabled=server.is_enabled,
        api_domain=server.api_domain,
        upload_enabled=server.upload_enabled,
    )


def _check_sid_free(session: SessionDep, server_sid: str, exclude_id: int | None = None) -> None:
    existing = session.exec(
        select(ServerInfo).where(ServerInfo.server_sid == server_sid)
    ).first()
    if existing is not None and existing.server_id != exclude_id:
        raise HTTPException(
            status_code=400, detail=f"A server with server_sid '{server_sid}' already exists"
        )


def _normalize_domain(value: str) -> str:
    """
    Both server_domain and api_domain are stored bare (no scheme, no
    trailing slash) - code that needs a full URL adds the scheme back (see
    app.media.resolve_server_link, app.uploaders.base.normalize_base_url).
    Stripping here means it doesn't matter whether whoever's entering it
    pastes "https://example.com" or "example.com" - it lands the same way.
    """
    domain = value.strip()
    for prefix in ("https://", "http://"):
        if domain.lower().startswith(prefix):
            domain = domain[len(prefix) :]
            break
    return domain.rstrip("/")


@router.get("/")
def list_servers(session: SessionDep) -> ServerAdminListPublic:
    servers = session.exec(
        select(ServerInfo).order_by(col(ServerInfo.server_order).asc())
    ).all()
    return ServerAdminListPublic(data=[_to_public(s) for s in servers])


@router.post("/", status_code=201)
def create_server(session: SessionDep, body: ServerCreate) -> ServerAdminPublic:
    _check_sid_free(session, body.server_sid)

    data = body.model_dump()
    data["server_domain"] = _normalize_domain(data["server_domain"])
    if data.get("api_domain"):
        data["api_domain"] = _normalize_domain(data["api_domain"])

    server = ServerInfo(**data)
    session.add(server)
    session.commit()
    session.refresh(server)
    return _to_public(server)


@router.patch("/{server_id}")
def update_server(
    session: SessionDep, server_id: int, body: ServerUpdate
) -> ServerAdminPublic:
    server = session.get(ServerInfo, server_id)
    if server is None:
        raise HTTPException(status_code=404, detail="Server not found")

    updates = body.model_dump(exclude_unset=True)
    if "server_sid" in updates:
        _check_sid_free(session, updates["server_sid"], exclude_id=server_id)
    if updates.get("server_domain"):
        updates["server_domain"] = _normalize_domain(updates["server_domain"])
    if updates.get("api_domain"):
        updates["api_domain"] = _normalize_domain(updates["api_domain"])

    for field, value in updates.items():
        setattr(server, field, value)

    session.add(server)
    session.commit()
    session.refresh(server)
    return _to_public(server)


@router.delete("/{server_id}", status_code=204)
def delete_server(session: SessionDep, server_id: int) -> None:
    server = session.get(ServerInfo, server_id)
    if server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    session.delete(server)
    session.commit()
