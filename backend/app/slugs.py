import re
from typing import Any

from sqlmodel import Session, select


def slugify(value: str, fallback: str = "item") -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or fallback


def ensure_unique_slug(session: Session, base_slug: str, model: Any, column: Any) -> str:
    candidate = base_slug
    suffix = 2
    while session.exec(select(model).where(column == candidate)).first() is not None:
        candidate = f"{base_slug}-{suffix}"
        suffix += 1
    return candidate
