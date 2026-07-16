"""
One-time migration: blog posts + comments -> deadbase Posts/Comments/PostTags/SeasonDubs.

Source: blog-db (MariaDB, see ../../compose.migration.yaml, `deadtoons` schema)
Target: deadbase (Postgres)

Safe to re-run: a post is skipped entirely (post + its comments) if a Posts row
already exists for the anime/season it resolves to. Anomalies (unmappable
posts, ambiguous categories, broken comment threads) are collected and printed
as a report at the end rather than failing the run.
"""

import itertools
import logging
import re
from datetime import UTC, datetime
from typing import Any

import pymysql
import pymysql.cursors
from sqlmodel import Session, select

from app.core.db import engine
from app.models import (
    Animes,
    Comments,
    CommentStatus,
    Languages,
    OttPlatforms,
    Posts,
    PostStatus,
    PostTags,
    SeasonDubs,
    Seasons,
    Tags,
    User,
)

BLOG_DB_HOST = "127.0.0.1"
BLOG_DB_PORT = 3307
BLOG_DB_USER = "root"
BLOG_DB_PASSWORD = "migration"
BLOG_DB_NAME = "deadtoons"

OLD_IMAGE_DOMAIN = "https://deadtoons.sbs"
IMAGE_DOMAIN = "https://image.deadbase.host/uploads"

SHORTCODE_RE = re.compile(
    r'\[deadbase animeid="(\d+)"(?: season="(\w+)")? type="(\w+)"(?: honly="(\d)")?\]'
)
DEADBASE_ID_RE = re.compile(r"^(\d+)-s(\d+)$")

AUTHOR_EMAIL_BY_BLOG_ID = {
    1: "zylithdti@gmail.com",
    3: "tw4all@deadtoons.internal",
    4: "tpx@deadtoons.internal",
    5: "atozcartoonist@deadtoons.internal",
}

STATUS_CATS = {14: PostStatus.ONGOING, 16: PostStatus.COMPLETED}

OTT_CATS = {
    3: "Cartoon Network",
    13: "Crunchyroll",
    17: "ZeeCafe",
    20: "Netflix",
    25: "Disney",
    26: "ETV",
    41: "Sony Yay",
    42: "Amazon",
    45: "Hungama",
    52: "Muse India",
    108: "Kidzone Pakistan",
    127: "Voot Kids",
    164: "Jio Cinema",
    310: "Nickelodeon",
    400: "Pogo",
    415: "Apple+",
}
SONIC_NICK_CAT_ID = 128
SONIC_NICK_OTT_NAMES = ("Sonic", "Nick")

LANGUAGE_CATS = {
    292: "Tamil",
    293: "Telugu",
    294: "Malayalam",
    392: "Urdu",
    394: "Kannada",
    406: "Bengali",
}

TAG_CATS = {
    102: "eng-subbed",
    260: "live-action",
    205: "special",
    408: "ova",
    6: "marvel",
}

COMMENT_STATUS_MAP = {"1": CommentStatus.APPROVED, "pending": CommentStatus.PENDING}

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def decode_row(row: dict[str, Any]) -> dict[str, Any]:
    """Some historical rows contain invalid UTF-8 byte sequences; replace rather than crash."""
    return {
        key: value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value
        for key, value in row.items()
    }


def resolve_backdrop_url(file_path: str, is_new: bool) -> str:
    if is_new:
        return f"{IMAGE_DOMAIN}/w780/{file_path.lstrip('/')}"
    dirname, _, filename = file_path.rpartition("/")
    stem, dot, ext = filename.rpartition(".")
    resized = f"{stem}-640x360{dot}{ext}" if dot else f"{filename}-640x360"
    path = f"{dirname}/{resized}" if dirname else resized
    return f"{OLD_IMAGE_DOMAIN}/content/{path}"


def resolve_target(
    post: dict[str, Any], anomalies: list[str]
) -> tuple[str, int, int | None] | None:
    """Return (type, anime_id, season_number|None) or None if unresolvable."""
    deadbase_id = post["deadbase_id"]
    if post["is_dynamic"] and deadbase_id:
        match = DEADBASE_ID_RE.match(deadbase_id)
        if match:
            return "tv", int(match.group(1)), int(match.group(2))
        anomalies.append(f"post {post['id']}: is_dynamic with unparsable deadbase_id {deadbase_id!r}")

    content = post["content"] or ""
    match = SHORTCODE_RE.search(content)
    if not match:
        anomalies.append(f"post {post['id']} ({post['title']!r}): no shortcode and no usable deadbase_id")
        return None

    anime_id, season, type_, _honly = match.groups()
    if type_ == "movie":
        return "movie", int(anime_id), None
    if season is None or not season.isdigit():
        anomalies.append(
            f"post {post['id']}: shortcode type={type_!r} has non-single-season value season={season!r}"
        )
        return None
    return "tv", int(anime_id), int(season)


def main() -> None:
    anomalies: list[str] = []
    blog = pymysql.connect(
        host=BLOG_DB_HOST,
        port=BLOG_DB_PORT,
        user=BLOG_DB_USER,
        password=BLOG_DB_PASSWORD,
        database=BLOG_DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        use_unicode=False,
    )

    with Session(engine) as session, blog.cursor() as cur:
        cur.execute(
            "SELECT id, title, slug, is_dynamic, deadbase_id, pubDate, author, "
            "content, sticky, views, thumbnail FROM posts WHERE post_type='post'"
        )
        posts = [decode_row(row) for row in cur.fetchall()]

        cur.execute("SELECT id, file_path, is_new FROM images")
        images_by_id = {row["id"]: decode_row(row) for row in cur.fetchall()}

        cur.execute("SELECT post_id, category_id FROM post_categories")
        cats_by_post: dict[int, list[int]] = {}
        for row in cur.fetchall():
            cats_by_post.setdefault(row["post_id"], []).append(row["category_id"])

        migrated = 0
        skipped_existing = 0

        for post in posts:
            target = resolve_target(post, anomalies)
            if target is None:
                continue
            kind, anime_id, season_number = target

            anime = session.exec(
                select(Animes).where(Animes.anime_id == anime_id)
            ).first()
            if not anime:
                anomalies.append(f"post {post['id']}: anime_id {anime_id} not found in deadbase")
                continue

            season: Seasons | None = None
            if kind == "tv":
                season = session.exec(
                    select(Seasons).where(
                        Seasons.anime_id == anime_id,
                        Seasons.season_number == season_number,
                    )
                ).first()
                if not season:
                    anomalies.append(
                        f"post {post['id']}: season {season_number} of anime_id {anime_id} not found"
                    )
                    continue
                if anime.type != "tv":
                    anomalies.append(
                        f"post {post['id']}: shortcode says tv but anime_id {anime_id} type is {anime.type!r}"
                    )
                    continue
            elif anime.type != "movie":
                anomalies.append(
                    f"post {post['id']}: shortcode says movie but anime_id {anime_id} type is {anime.type!r}"
                )
                continue

            existing = session.exec(
                select(Posts).where(
                    Posts.anime_id == (anime_id if kind == "movie" else None),
                    Posts.season_id == (season.season_id if season else None),
                )
            ).first()
            if existing:
                skipped_existing += 1
                continue

            cat_ids = cats_by_post.get(post["id"], [])
            status = PostStatus.COMPLETED
            for cid in cat_ids:
                if cid in STATUS_CATS:
                    status = STATUS_CATS[cid]
                    break

            backdrop_img = None
            image = images_by_id.get(post["thumbnail"])
            if image:
                backdrop_img = resolve_backdrop_url(image["file_path"], bool(image["is_new"]))

            author_email = AUTHOR_EMAIL_BY_BLOG_ID.get(post["author"])
            author = None
            if author_email:
                author = session.exec(select(User).where(User.email == author_email)).first()

            new_post = Posts(
                anime_id=anime_id if kind == "movie" else None,
                season_id=season.season_id if season else None,
                title=post["title"] or "",
                slug=post["slug"] or f"post-{post['id']}",
                backdrop_img=backdrop_img,
                status=status,
                sticky=bool(post["sticky"]),
                views=post["views"] or 0,
                author_id=author.id if author else None,
                last_updated=(post["pubDate"] or datetime.now(UTC)),
            )
            session.add(new_post)
            session.flush()

            for cid in cat_ids:
                if cid in TAG_CATS:
                    tag = session.exec(
                        select(Tags).where(Tags.slug == TAG_CATS[cid])
                    ).first()
                    if tag:
                        session.add(PostTags(post_id=new_post.id, tag_id=tag.id))

            if kind == "tv" and season:
                ott_names = []
                for cid in cat_ids:
                    if cid in OTT_CATS:
                        ott_names.append(OTT_CATS[cid])
                    elif cid == SONIC_NICK_CAT_ID:
                        ott_names.extend(SONIC_NICK_OTT_NAMES)
                language_names = [LANGUAGE_CATS[cid] for cid in cat_ids if cid in LANGUAGE_CATS]

                for ott_name, lang_name in itertools.product(ott_names, language_names):
                    ott = session.exec(
                        select(OttPlatforms).where(OttPlatforms.ott_name == ott_name)
                    ).first()
                    lang = session.exec(
                        select(Languages).where(Languages.language_name == lang_name)
                    ).first()
                    if not ott or not lang:
                        anomalies.append(
                            f"post {post['id']}: could not resolve ott={ott_name!r} lang={lang_name!r}"
                        )
                        continue
                    exists = session.exec(
                        select(SeasonDubs).where(
                            SeasonDubs.season_id == season.season_id,
                            SeasonDubs.ott_id == ott.ott_id,
                            SeasonDubs.language_id == lang.language_id,
                        )
                    ).first()
                    if not exists:
                        session.add(
                            SeasonDubs(
                                season_id=season.season_id,
                                ott_id=ott.ott_id,
                                language_id=lang.language_id,
                            )
                        )

            with blog.cursor() as ccur:
                ccur.execute(
                    "SELECT com_id, parent_id, com_author, com_email, com_author_url, "
                    "com_date, com_content, com_status FROM comments "
                    "WHERE post_id=%s ORDER BY com_id ASC",
                    (post["id"],),
                )
                blog_comments = [decode_row(row) for row in ccur.fetchall()]

            old_to_new: dict[int, int] = {}
            for c in blog_comments:
                new_parent_id = None
                if c["parent_id"] is not None:
                    new_parent_id = old_to_new.get(c["parent_id"])
                    if new_parent_id is None:
                        anomalies.append(
                            f"post {post['id']} comment {c['com_id']}: parent {c['parent_id']} not migrated, flattening to top-level"
                        )
                status_value = COMMENT_STATUS_MAP.get(str(c["com_status"]))
                if status_value is None:
                    anomalies.append(
                        f"post {post['id']} comment {c['com_id']}: unknown com_status {c['com_status']!r}, defaulting to pending"
                    )
                    status_value = CommentStatus.PENDING
                new_comment = Comments(
                    post_id=new_post.id,
                    parent_id=new_parent_id,
                    author_name=c["com_author"] or "",
                    author_email=c["com_email"] or "",
                    author_url=c["com_author_url"] or None,
                    body=c["com_content"] or "",
                    created_at=c["com_date"] or datetime.now(UTC),
                    status=status_value,
                )
                session.add(new_comment)
                session.flush()
                assert new_comment.id is not None
                old_to_new[c["com_id"]] = new_comment.id

            session.commit()
            migrated += 1

    blog.close()

    logger.info("migrated: %d", migrated)
    logger.info("skipped (already migrated): %d", skipped_existing)
    logger.info("anomalies: %d", len(anomalies))
    for a in anomalies:
        logger.info("  - %s", a)


if __name__ == "__main__":
    main()
