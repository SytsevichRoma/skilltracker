"""Create tasks table

Revision ID: 159c77ad120c
Revises: b42f8988a4a3
Create Date: 2026-01-21 21:21:28.773416

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '159c77ad120c'
down_revision = 'b42f8988a4a3'
branch_labels = None
depends_on = None


def upgrade():
    # Legacy migration superseded by e31466bfaefe_init.
    pass


def downgrade():
    # Legacy migration superseded by e31466bfaefe_init.
    pass
