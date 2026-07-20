import httpx

from app.models import ServerInfo
from app.uploaders.base import UploadError, normalize_base_url


def upload(server: ServerInfo, gdrive_id: str) -> str:
    """
    Mirrors a Google Drive file onto FilePress. Returns the FilePress file
    id (used as the LinkServers.slug) on success. Only key + gdrive id are
    sent - every other field FilePress's /file/add accepts is optional and
    unused here.
    """
    if not server.api_domain or not server.api:
        raise UploadError(
            f"Server '{server.server_sid}' has no api_domain/api key configured",
            retryable=False,
        )

    url = f"{normalize_base_url(server.api_domain)}/api/v1/file/add"
    payload = {"key": server.api, "id": gdrive_id}

    try:
        response = httpx.post(url, json=payload, timeout=30, follow_redirects=True)
    except httpx.HTTPError as exc:
        raise UploadError(f"FilePress request failed: {exc}") from exc

    if response.status_code == 429 or response.status_code >= 500:
        raise UploadError(f"FilePress returned HTTP {response.status_code}")
    if response.status_code >= 400:
        raise UploadError(
            f"FilePress returned HTTP {response.status_code}", retryable=False
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise UploadError(
            "FilePress returned a non-JSON response", retryable=False
        ) from exc

    if data.get("statusCode") != 200:
        raise UploadError(str(data.get("statusText") or "FilePress rejected the upload"))

    file_id = (data.get("data") or {}).get("_id")
    if not file_id:
        raise UploadError("FilePress response missing data._id", retryable=False)

    return str(file_id)
