"""add bucket image source

Revision ID: 066d9e45ad33
Revises: 60c101526c5d
Create Date: 2026-07-19 10:18:48.015572

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '066d9e45ad33'
down_revision = '60c101526c5d'
branch_labels = None
depends_on = None


def upgrade():
    # These enum types store lowercase values (legacy-migrated columns),
    # unlike the newer hand-written enums in this project which store
    # uppercase names - match the existing 'tmdb'/'local'/'url' convention.
    # ADD VALUE can't run inside the implicit migration transaction.
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE animes_backdrop_source ADD VALUE IF NOT EXISTS 'bucket'")
        op.execute("ALTER TYPE animes_poster_source ADD VALUE IF NOT EXISTS 'bucket'")
        op.execute("ALTER TYPE seasons_poster_source ADD VALUE IF NOT EXISTS 'bucket'")


def downgrade():
    # Postgres can't drop a single enum value without rebuilding the type
    # and every column using it - not worth it for an additive, otherwise
    # unused value. No-op.
    pass
