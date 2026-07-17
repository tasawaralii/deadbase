import re

from app.models import CommentStatus

# Ported from the old blog's comment handler: URLs get held for review, Cyrillic
# text and this known spam-bot honeypot domain get rejected outright.
SPAM_TERMS = ("https://", "http://", "url")
BLOCKED_EMAIL_DOMAINS = ("testing-your-form.info",)
CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")


def is_blocked_email(email: str) -> bool:
    return any(domain in email for domain in BLOCKED_EMAIL_DOMAINS)


def is_rejected_body(body: str) -> bool:
    return bool(CYRILLIC_RE.search(body))


def initial_status(body: str) -> CommentStatus:
    if any(term in body for term in SPAM_TERMS):
        return CommentStatus.PENDING
    return CommentStatus.APPROVED
