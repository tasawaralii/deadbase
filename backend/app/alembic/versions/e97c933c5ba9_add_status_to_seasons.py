"""add status to seasons

Revision ID: e97c933c5ba9
Revises: 066d9e45ad33
Create Date: 2026-07-20 00:01:58.559920

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'e97c933c5ba9'
down_revision = '066d9e45ad33'
branch_labels = None
depends_on = None


season_status_enum = postgresql.ENUM('ongoing', 'completed', name='season_status')


def upgrade():
    season_status_enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        'seasons',
        sa.Column(
            'status',
            postgresql.ENUM('ongoing', 'completed', name='season_status', create_type=False),
            server_default=sa.text("'ongoing'"),
            nullable=False,
        ),
    )


def downgrade():
    op.drop_column('seasons', 'status')
    season_status_enum.drop(op.get_bind(), checkfirst=True)
