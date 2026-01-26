"""Add completed_at to task

Revision ID: 6f4c2a0f2b3b
Revises: 340a297ef61d
Create Date: 2026-02-04 10:12:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6f4c2a0f2b3b'
down_revision = '340a297ef61d'
branch_labels = None
depends_on = None


def upgrade():
    # Legacy migration superseded by e31466bfaefe_init.
    pass


def downgrade():
    # Legacy migration superseded by e31466bfaefe_init.
    pass
