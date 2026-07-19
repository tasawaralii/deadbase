import re

from sqlmodel import Session, col, select

from app.models import Qualities

_RESOLUTION_RE = re.compile(r"\b(360p|480p|512p|576p|720p|1080p|2160p)\b", re.IGNORECASE)
_HEVC_RE = re.compile(r"x265|hevc|10bit", re.IGNORECASE)
_HQ_RE = re.compile(r"\bHQ\b", re.IGNORECASE)

# Tried in order against each filename rather than requiring the author to
# pick a mode upfront (the legacy admin required this) - the patterns are
# distinct enough in practice that trying all of them is safe.
_EPISODE_NUMBER_PATTERNS = (
    re.compile(r"s\d{1,2}e(\d{2,4})", re.IGNORECASE),
    re.compile(r" \((\d{3})\) "),
    re.compile(r" E(\d{3}) "),
    re.compile(r"Part (\d{1,2})", re.IGNORECASE),
)


def find_quality(session: Session, filename: str) -> int | None:
    match = _RESOLUTION_RE.search(filename)
    if not match:
        return None
    resolution = int(match.group(1).lower().rstrip("p"))
    is_hevc = bool(_HEVC_RE.search(filename))
    is_hq = bool(_HQ_RE.search(filename))

    quality = session.exec(
        select(Qualities)
        .where(
            col(Qualities.quality_resolution) == resolution,
            col(Qualities.is_hevc) == is_hevc,
            col(Qualities.is_hq) == is_hq,
        )
        .order_by(col(Qualities.quality_order).asc())
    ).first()
    return quality.quality_id if quality else None


def find_episode_number(filename: str) -> int | None:
    for pattern in _EPISODE_NUMBER_PATTERNS:
        match = pattern.search(filename)
        if match:
            return int(match.group(1))
    return None
