def normalize_base_url(api_domain: str) -> str:
    """
    ServerInfo.api_domain is admin-entered and may or may not already
    include a scheme (e.g. "https://new2.filepress.baby" or just
    "fpgo.xyz") - normalize to a scheme-prefixed, no-trailing-slash base
    URL so uploaders can safely append a path.
    """
    domain = api_domain.strip().rstrip("/")
    if not domain.startswith(("http://", "https://")):
        domain = f"https://{domain}"
    return domain


class UploadError(Exception):
    """
    Raised by an uploader when mirroring a file to a server fails.
    retryable=True (default) means transient - network error, timeout,
    5xx, rate limit - worth retrying with backoff. retryable=False means
    permanent - missing config, bad file, rejected outright - retrying
    won't help, so app.link_upload skips straight to the terminal failed
    state instead of burning attempts on it.
    """

    def __init__(self, message: str, *, retryable: bool = True) -> None:
        super().__init__(message)
        self.retryable = retryable
