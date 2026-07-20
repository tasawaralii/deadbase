"""add tv value to content_content_type enum

Revision ID: 7bacd26b5e7e
Revises: e97c933c5ba9
Create Date: 2026-07-20 09:08:43.705847

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '7bacd26b5e7e'
down_revision = 'e97c933c5ba9'
branch_labels = None
depends_on = None


def upgrade():
    # Postgres won't let a new enum value be used in the same transaction
    # it's added in - this migration only adds it, the backfill that uses
    # it lives in the next migration so it runs in its own transaction.
    op.execute("ALTER TYPE content_content_type ADD VALUE IF NOT EXISTS 'tv'")


def downgrade():
    # Postgres has no DROP VALUE for enums - removing 'tv' would require
    # rebuilding the type (rename old, create new, cast every column over,
    # drop old). Not worth it for a downgrade path; leaving the value in
    # place is harmless if this migration is ever rolled back.
    pass
