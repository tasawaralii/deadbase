from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlmodel import col, select

from app.api.deps import SessionDep, VisitorId
from app.media import resolve_server_link
from app.models import LinkServers, LinkShorteners, Message, ShortenerAttempts
from app.schemas.unlock import (
    ReportRequest,
    ShortenerOption,
    StartUnlockRequest,
    StartUnlockResponse,
    UnlockStatus,
)
from app.unlock import (
    TOKEN_VALIDITY,
    generate_token,
    get_unlock_config,
    maybe_auto_disable,
    record_download_event,
    reported_shortener_ids,
    resolve_shortener_url,
    solved_shortener_ids,
)

router = APIRouter(prefix="/unlock")


def _get_link_server(session: SessionDep, link_server_id: int) -> LinkServers:
    link_server = session.get(LinkServers, link_server_id)
    if not link_server:
        raise HTTPException(status_code=404, detail="Link not found")
    return link_server


def _resolve_url(link_server: LinkServers) -> str:
    url = resolve_server_link(
        link_server.server.server_sid,
        link_server.server.server_domain,
        link_server.slug,
    )
    if not url:
        raise HTTPException(status_code=404, detail="Link not available")
    return url


@router.get("/callback")
def unlock_callback(session: SessionDep, token: str) -> RedirectResponse:
    attempt = session.exec(
        select(ShortenerAttempts).where(ShortenerAttempts.token == token)
    ).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Invalid token")
    if attempt.solved_at is not None:
        raise HTTPException(status_code=400, detail="Token already used")
    if datetime.now(UTC) - attempt.created_at > TOKEN_VALIDITY:
        raise HTTPException(status_code=400, detail="Token expired")

    attempt.solved_at = datetime.now(UTC)
    session.add(attempt)
    session.commit()

    # Every solve immediately unlocks the file it was solved for - that's the
    # reward for solving it. The required-count threshold (see unlock_status)
    # is a separate bonus: once hit, later files skip the shortener entirely.
    link_server = _get_link_server(session, attempt.link_server_id)
    url = _resolve_url(link_server)
    record_download_event(
        session, attempt.visitor_id, attempt.link_server_id, attempt.shortener_id
    )
    return RedirectResponse(url)


@router.get("/{link_server_id}")
def unlock_status(
    session: SessionDep, visitor_id: VisitorId, link_server_id: int
) -> UnlockStatus:
    link_server = _get_link_server(session, link_server_id)
    config = get_unlock_config(session)
    solved_ids = solved_shortener_ids(session, visitor_id)

    if len(solved_ids) >= config.required_solves:
        url = _resolve_url(link_server)
        record_download_event(session, visitor_id, link_server_id, via_shortener_id=None)
        return UnlockStatus(unlocked=True, url=url)

    reported_ids = reported_shortener_ids(session, visitor_id)
    shorteners = session.exec(
        select(LinkShorteners)
        .where(col(LinkShorteners.is_enabled) == True)  # noqa: E712
        .order_by(col(LinkShorteners.sort_order).asc())
    ).all()

    return UnlockStatus(
        unlocked=False,
        solved=len(solved_ids),
        required=config.required_solves,
        shorteners=[
            ShortenerOption(
                id=s.id,
                name=s.name,
                message=s.message,
                how_to_video_url=s.how_to_video_url,
                logo_url=s.logo_url,
                already_solved=s.id in solved_ids,
                reported=s.id in reported_ids,
            )
            for s in shorteners
        ],
    )


@router.post("/{link_server_id}/start")
def start_unlock(
    session: SessionDep,
    visitor_id: VisitorId,
    link_server_id: int,
    body: StartUnlockRequest,
    request: Request,
) -> StartUnlockResponse:
    _get_link_server(session, link_server_id)

    shortener = session.get(LinkShorteners, body.shortener_id)
    if not shortener or not shortener.is_enabled:
        raise HTTPException(status_code=404, detail="Shortener not found")

    if body.shortener_id in solved_shortener_ids(session, visitor_id):
        raise HTTPException(
            status_code=400, detail="Already solved this shortener recently"
        )

    token = generate_token()
    attempt = ShortenerAttempts(
        token=token,
        visitor_id=visitor_id,
        shortener_id=body.shortener_id,
        link_server_id=link_server_id,
    )
    session.add(attempt)
    session.commit()
    session.refresh(attempt)

    callback_url = str(request.url_for("unlock_callback")) + f"?token={token}"
    redirect_url = resolve_shortener_url(shortener, callback_url)
    return StartUnlockResponse(redirect_url=redirect_url)


@router.post("/{link_server_id}/report")
def report_shortener(
    session: SessionDep,
    visitor_id: VisitorId,
    link_server_id: int,
    body: ReportRequest,
) -> Message:
    attempt = session.exec(
        select(ShortenerAttempts)
        .where(
            ShortenerAttempts.visitor_id == visitor_id,
            ShortenerAttempts.link_server_id == link_server_id,
            ShortenerAttempts.shortener_id == body.shortener_id,
        )
        .order_by(col(ShortenerAttempts.created_at).desc())
    ).first()
    if not attempt:
        raise HTTPException(
            status_code=404, detail="No attempt found for this shortener on this link"
        )
    if attempt.solved_at is not None:
        raise HTTPException(
            status_code=400, detail="Cannot report an attempt that was solved"
        )
    if attempt.reported_at is not None:
        raise HTTPException(status_code=400, detail="Already reported")

    attempt.reported_at = datetime.now(UTC)
    attempt.report_reason = body.reason
    session.add(attempt)
    session.commit()
    maybe_auto_disable(session, body.shortener_id)
    return Message(message="Reported")
