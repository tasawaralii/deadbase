"""One-time seed for the blog migration: author User rows, missing OttPlatforms/Languages, kept Tags."""

import secrets

from sqlmodel import Session, select

from app.core.db import engine
from app.core.security import get_password_hash
from app.models import Languages, OttPlatforms, Tags, User

AUTHORS = [
    {"email": "zylithdti@gmail.com", "full_name": "Admin", "is_superuser": True},
    {"email": "tw4all@deadtoons.internal", "full_name": "Toon World", "is_superuser": False},
    {"email": "tpx@deadtoons.internal", "full_name": "Tpx", "is_superuser": False},
    {"email": "atozcartoonist@deadtoons.internal", "full_name": "AtoZCartoonist", "is_superuser": False},
]

NEW_OTT_PLATFORMS = [
    ("zeecafe", "ZeeCafe"),
    ("etv", "ETV"),
    ("sony-yay", "Sony Yay"),
    ("voot-kids", "Voot Kids"),
    ("nickelodeon", "Nickelodeon"),
    ("pogo", "Pogo"),
    ("apple-plus", "Apple+"),
    ("kidzone-pakistan", "Kidzone Pakistan"),
    ("jio-cinema", "Jio Cinema"),
    ("sonic", "Sonic"),
    ("nick", "Nick"),
]

NEW_LANGUAGES = [
    ("malayalam", "Malayalam"),
    ("urdu", "Urdu"),
    ("kannada", "Kannada"),
    ("bengali", "Bengali"),
]

KEPT_TAGS = [
    ("eng-subbed", "Eng Subbed"),
    ("live-action", "Live Action"),
    ("special", "Special"),
    ("ova", "OVA"),
    ("marvel", "Marvel"),
]


def main() -> None:
    with Session(engine) as session:
        for author in AUTHORS:
            existing = session.exec(
                select(User).where(User.email == author["email"])
            ).first()
            if existing:
                print(f"skip existing user {author['email']}")
                continue
            session.add(
                User(
                    email=author["email"],
                    full_name=author["full_name"],
                    hashed_password=get_password_hash(secrets.token_urlsafe(24)),
                    is_active=True,
                    is_superuser=author["is_superuser"],
                )
            )
            print(f"created user {author['email']}")

        for sid, name in NEW_OTT_PLATFORMS:
            existing = session.exec(
                select(OttPlatforms).where(OttPlatforms.ott_name == name)
            ).first()
            if existing:
                print(f"skip existing ott {name}")
                continue
            session.add(OttPlatforms(ott_sid=sid, ott_name=name))
            print(f"created ott {name}")

        for sid, name in NEW_LANGUAGES:
            existing = session.exec(
                select(Languages).where(Languages.language_name == name)
            ).first()
            if existing:
                print(f"skip existing language {name}")
                continue
            session.add(Languages(language_sid=sid, language_name=name))
            print(f"created language {name}")

        for slug, name in KEPT_TAGS:
            existing = session.exec(select(Tags).where(Tags.slug == slug)).first()
            if existing:
                print(f"skip existing tag {name}")
                continue
            session.add(Tags(slug=slug, name=name))
            print(f"created tag {name}")

        session.commit()


if __name__ == "__main__":
    main()
