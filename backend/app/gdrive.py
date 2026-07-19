import re
from typing import Any

import httpx
from fastapi import HTTPException

from app.core.config import settings

_BASE_URL = "https://www.googleapis.com/drive/v3"
_FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"

_FILE_ID_RE = re.compile(r"/d/([a-zA-Z0-9_-]+)")
_FOLDER_ID_RE = re.compile(r"/folders/([a-zA-Z0-9_-]+)")


def extract_file_id(value: str) -> str:
    """Accepts either a full Drive file URL or a bare id, returns the id."""
    match = _FILE_ID_RE.search(value)
    return match.group(1) if match else value.strip()


def extract_folder_id(value: str) -> str:
    """Accepts either a full Drive folder URL or a bare id, returns the id."""
    match = _FOLDER_ID_RE.search(value)
    return match.group(1) if match else value.strip()


def _get(path: str, params: dict[str, str]) -> dict[str, Any]:
    if not settings.GOOGLE_API_KEY:
        raise HTTPException(status_code=503, detail="Google API key is not configured")

    query = {"key": settings.GOOGLE_API_KEY, **params}
    try:
        response = httpx.get(f"{_BASE_URL}{path}", params=query, timeout=15)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502, detail="Could not reach Google Drive"
        ) from exc

    if response.status_code == 404:
        raise HTTPException(
            status_code=400, detail="Google Drive file not found - check the link"
        )
    if response.status_code == 403:
        raise HTTPException(
            status_code=400,
            detail="Google Drive file is private or inaccessible - check sharing permissions",
        )
    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail="Google Drive request failed")

    result: dict[str, Any] = response.json()
    return result


def fetch_file_metadata(file_id: str) -> dict[str, Any]:
    fields = "id,name,size,mimeType,owners(emailAddress),videoMediaMetadata(durationMillis)"
    return _get(f"/files/{file_id}", {"fields": fields})


def list_folder_files(folder_id: str) -> list[dict[str, Any]]:
    """Lists all non-folder files directly inside a Drive folder, following
    pagination (the legacy PHP version didn't, so large seasons could get
    silently truncated there)."""
    files: list[dict[str, Any]] = []
    page_token: str | None = None
    while True:
        params = {
            "q": f"'{folder_id}' in parents",
            "orderBy": "name",
            "fields": "nextPageToken,files(id,name,mimeType)",
            "pageSize": "1000",
        }
        if page_token:
            params["pageToken"] = page_token

        data = _get("/files", params)
        files.extend(
            f for f in data.get("files", []) if f.get("mimeType") != _FOLDER_MIME_TYPE
        )
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return files
