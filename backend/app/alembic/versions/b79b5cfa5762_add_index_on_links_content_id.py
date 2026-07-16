"""add index on links content_id

Revision ID: b79b5cfa5762
Revises: 4ec55cb094af
Create Date: 2026-07-15 22:07:11.574896

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'b79b5cfa5762'
down_revision = '4ec55cb094af'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('ix_links_content_id', 'links', ['content_id'], unique=False)


def downgrade():
    op.drop_index('ix_links_content_id', table_name='links')
