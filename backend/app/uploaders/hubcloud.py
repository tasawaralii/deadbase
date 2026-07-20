import httpx

from app.models import ServerInfo
from app.uploaders.base import UploadError, normalize_base_url


def upload(server: ServerInfo, gdrive_id: str) -> str:
    """
    Mirrors a Google Drive file onto HubCloud. Returns the HubCloud slug
    (used as LinkServers.slug) on success.
    """
    if not server.api_domain or not server.api:
        raise UploadError(
            f"Server '{server.server_sid}' has no api_domain/api key configured",
            retryable=False,
        )

    url = f"{normalize_base_url(server.api_domain)}/drive/shareapi.php"
    params = {"key": server.api, "link_add": gdrive_id}

    try:
        response = httpx.get(url, params=params, timeout=30, follow_redirects=True)
    except httpx.HTTPError as exc:
        raise UploadError(f"HubCloud request failed: {exc}") from exc

    if response.status_code == 429 or response.status_code >= 500:
        raise UploadError(f"HubCloud returned HTTP {response.status_code}")
    if response.status_code >= 400:
        raise UploadError(
            f"HubCloud returned HTTP {response.status_code}", retryable=False
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise UploadError(
            "HubCloud returned a non-JSON response", retryable=False
        ) from exc

    if str(data.get("status")) != "200":
        raise UploadError(str(data.get("data") or "HubCloud rejected the upload"))

    slug = data.get("data")
    if not slug:
        raise UploadError("HubCloud response missing data", retryable=False)

    return str(slug)
