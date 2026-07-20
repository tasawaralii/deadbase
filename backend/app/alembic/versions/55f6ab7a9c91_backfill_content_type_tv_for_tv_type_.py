"""backfill content_type=tv for tv-type animes

Revision ID: 55f6ab7a9c91
Revises: 7bacd26b5e7e
Create Date: 2026-07-20 09:09:58.638295

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '55f6ab7a9c91'
down_revision = '7bacd26b5e7e'
branch_labels = None
depends_on = None


def upgrade():
    # Every Animes row got its Content row created as content_type='movie'
    # regardless of the anime's actual type (content_id is NOT NULL, so a
    # placeholder Content row was always needed) - tv-type anime never
    # actually use it for links/comments/view-tracking. Retag those rows
    # 'tv' so every existing "== MOVIE means attachable" check excludes
    # them automatically, closing off attaching links/comments directly to
    # a tv anime's own content_id instead of its episodes/packs.
    op.execute(
        """
        UPDATE content
        SET content_type = 'tv'
        FROM animes
        WHERE animes.content_id = content.id
          AND animes.type = 'tv'
          AND content.content_type = 'movie'
        """
    )


def downgrade():
    op.execute(
        """
        UPDATE content
        SET content_type = 'movie'
        FROM animes
        WHERE animes.content_id = content.id
          AND animes.type = 'tv'
          AND content.content_type = 'tv'
        """
    )
