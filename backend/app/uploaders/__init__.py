from collections.abc import Callable

from app.models import ServerInfo
from app.uploaders import filepress, hubcloud
from app.uploaders.base import UploadError

# server_sid -> upload(server, gdrive_id) -> slug. Add a new server by
# writing app/uploaders/<name>.py with this same signature and registering
# it here - app.link_upload dispatches through this dict, no per-server
# branching in the orchestration/retry logic.
Uploader = Callable[[ServerInfo, str], str]

UPLOADERS: dict[str, Uploader] = {
    "filepress": filepress.upload,
    "hubcloud": hubcloud.upload,
}

__all__ = ["UPLOADERS", "UploadError", "Uploader"]
