import decimal
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, select

from app.api.deps import CurrentAuthor, SessionDep, get_current_author
from app.content import resolve_anime_id_for_content
from app.filename_parsing import find_episode_number, find_quality
from app.gdrive import (
    extract_file_id,
    extract_folder_id,
    fetch_file_metadata,
    list_folder_files,
)
from app.models import Content, Episodes, Links, Seasons, User
from app.permissions import require_anime_write_access
from app.schemas.admin_link import (
    GdriveFolderFile,
    GdriveFolderListing,
    LinkAdminListPublic,
    LinkAdminPublic,
    LinkBatchCreate,
    LinkBatchResult,
    LinkBatchResultItem,
    LinkBulkDeleteResult,
)

router = APIRouter(
    prefix="/content/{content_id}/links",
    tags=["admin"],
    dependencies=[Depends(get_current_author)],
)

# Deletion is keyed purely on link_id - content_id is already recoverable
# from the link itself (link.content_id), no need to carry it separately.
single_link_router = APIRouter(
    prefix="/links", tags=["admin"], dependencies=[Depends(get_current_author)]
)

season_links_router = APIRouter(
    prefix="/seasons/{season_id}/links",
    tags=["admin"],
    dependencies=[Depends(get_current_author)],
)

gdrive_router = APIRouter(
    prefix="/gdrive", tags=["admin"], dependencies=[Depends(get_current_author)]
)


def _get_content_with_access(session: SessionDep, author: User, content_id: int) -> Content:
    content = session.get(Content, content_id)
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found")
    anime_id = resolve_anime_id_for_content(session, content)
    if anime_id is None:
        raise HTTPException(status_code=404, detail="Content has no resolvable owner")
    require_anime_write_access(session, author, anime_id)
    return content


def _to_public(link: Links) -> LinkAdminPublic:
    return LinkAdminPublic(
        link_id=link.link_id,
        content_id=link.content_id,
        filename=link.filename,
        is_live=link.is_live,
        gdrive_email=link.gdrive_email,
        gdriveid=link.gdriveid,
        type=link.type,
        mimetype=link.mimetype,
        duration=link.duration,
        note=link.note,
        only_hindi=link.only_hindi,
        size=link.size,
        quality_id=link.quality_id,
        added_date=link.added_date,
        updated_date=link.updated_date,
    )


def _create_link_from_metadata(
    session: SessionDep,
    content_id: int,
    file_id: str,
    note: str,
    only_hindi: bool,
) -> Links:
    existing = session.exec(select(Links).where(Links.gdriveid == file_id)).first()
    if existing is not None:
        raise HTTPException(
            status_code=400, detail="A link for this Google Drive file already exists"
        )

    metadata = fetch_file_metadata(file_id)
    filename = metadata.get("name") or file_id
    owners = metadata.get("owners") or []
    gdrive_email = owners[0]["emailAddress"] if owners else ""
    size = metadata.get("size")
    video_meta = metadata.get("videoMediaMetadata") or {}

    now = datetime.now(UTC)
    link = Links(
        filename=filename,
        is_live=True,
        gdrive_email=gdrive_email,
        gdriveid=file_id,
        type=filename.rsplit(".", 1)[-1] if "." in filename else "",
        mimetype=metadata.get("mimeType") or "unknown",
        duration=int(video_meta.get("durationMillis", 0)),
        note=note,
        only_hindi=only_hindi,
        added_date=now,
        updated_date=now,
        content_id=content_id,
        size=decimal.Decimal(size) if size is not None else None,
        quality_id=find_quality(session, filename),
    )
    session.add(link)
    session.commit()
    session.refresh(link)
    return link


@router.get("/")
def list_links(
    session: SessionDep, author: CurrentAuthor, content_id: int
) -> LinkAdminListPublic:
    _get_content_with_access(session, author, content_id)
    links = session.exec(select(Links).where(Links.content_id == content_id)).all()
    return LinkAdminListPublic(data=[_to_public(link) for link in links])


@router.post("/")
def create_links(
    session: SessionDep, author: CurrentAuthor, content_id: int, body: LinkBatchCreate
) -> LinkBatchResult:
    """
    One or more gdrive links for the same content (e.g. every quality of a
    movie, or every file in a pack) in a single call - the frontend never
    needs to loop one request per quality/file.
    """
    _get_content_with_access(session, author, content_id)

    results: list[LinkBatchResultItem] = []
    for url in body.gdrive_urls:
        try:
            file_id = extract_file_id(url)
            link = _create_link_from_metadata(
                session, content_id, file_id, body.note, body.only_hindi
            )
            results.append(
                LinkBatchResultItem(gdrive_url=url, success=True, link=_to_public(link))
            )
        except HTTPException as exc:
            results.append(
                LinkBatchResultItem(gdrive_url=url, success=False, error=str(exc.detail))
            )

    return LinkBatchResult(results=results)


@router.delete("/")
def delete_all_links(
    session: SessionDep, author: CurrentAuthor, content_id: int
) -> LinkBulkDeleteResult:
    _get_content_with_access(session, author, content_id)
    links = session.exec(select(Links).where(Links.content_id == content_id)).all()
    count = len(links)
    for link in links:
        session.delete(link)
    session.commit()
    return LinkBulkDeleteResult(deleted_count=count)


@season_links_router.post("/batch")
def create_season_links_batch(
    session: SessionDep, author: CurrentAuthor, season_id: int, body: LinkBatchCreate
) -> LinkBatchResult:
    """
    For each gdrive link: fetch its metadata, auto-detect the episode number
    from the filename, and attach the link to that episode. One bad file
    (unmatched episode, private file, etc) is reported per-item rather than
    aborting the whole batch.
    """
    season = session.get(Seasons, season_id)
    if season is None:
        raise HTTPException(status_code=404, detail="Season not found")
    require_anime_write_access(session, author, season.anime_id)

    results: list[LinkBatchResultItem] = []
    for url in body.gdrive_urls:
        try:
            file_id = extract_file_id(url)
            metadata = fetch_file_metadata(file_id)
            filename = metadata.get("name") or file_id

            episode_number = find_episode_number(filename)
            if episode_number is None:
                results.append(
                    LinkBatchResultItem(
                        gdrive_url=url,
                        success=False,
                        error=f"Could not find an episode number in '{filename}'",
                    )
                )
                continue

            episode = session.exec(
                select(Episodes).where(
                    Episodes.season_id == season_id,
                    Episodes.episode_number == episode_number,
                )
            ).first()
            if episode is None:
                results.append(
                    LinkBatchResultItem(
                        gdrive_url=url,
                        success=False,
                        error=f"No episode {episode_number} in this season",
                    )
                )
                continue

            link = _create_link_from_metadata(
                session, episode.content_id, file_id, body.note, body.only_hindi
            )
            results.append(
                LinkBatchResultItem(gdrive_url=url, success=True, link=_to_public(link))
            )
        except HTTPException as exc:
            results.append(
                LinkBatchResultItem(gdrive_url=url, success=False, error=str(exc.detail))
            )

    return LinkBatchResult(results=results)


@season_links_router.delete("/")
def delete_all_season_episode_links(
    session: SessionDep, author: CurrentAuthor, season_id: int
) -> LinkBulkDeleteResult:
    season = session.get(Seasons, season_id)
    if season is None:
        raise HTTPException(status_code=404, detail="Season not found")
    require_anime_write_access(session, author, season.anime_id)

    episode_content_ids = session.exec(
        select(Episodes.content_id).where(Episodes.season_id == season_id)
    ).all()
    if not episode_content_ids:
        return LinkBulkDeleteResult(deleted_count=0)

    links = session.exec(
        select(Links).where(col(Links.content_id).in_(episode_content_ids))
    ).all()
    count = len(links)
    for link in links:
        session.delete(link)
    session.commit()
    return LinkBulkDeleteResult(deleted_count=count)


@gdrive_router.get("/folder")
def list_gdrive_folder(url: str) -> GdriveFolderListing:
    folder_id = extract_folder_id(url)
    files = list_folder_files(folder_id)
    return GdriveFolderListing(
        files=[
            GdriveFolderFile(
                file_id=f["id"],
                name=f["name"],
                url=f"https://drive.google.com/file/d/{f['id']}",
            )
            for f in files
        ]
    )


@single_link_router.delete("/{link_id}", status_code=204)
def delete_link(session: SessionDep, author: CurrentAuthor, link_id: int) -> None:
    link = session.get(Links, link_id)
    if link is None:
        raise HTTPException(status_code=404, detail="Link not found")

    content = session.get(Content, link.content_id)
    anime_id = resolve_anime_id_for_content(session, content) if content else None
    if anime_id is None:
        raise HTTPException(status_code=404, detail="Link has no resolvable owner")
    require_anime_write_access(session, author, anime_id)

    session.delete(link)
    session.commit()
