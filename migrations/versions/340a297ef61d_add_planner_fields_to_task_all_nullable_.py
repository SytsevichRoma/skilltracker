"""Add planner fields to task (all nullable for sqlite)

Revision ID: 340a297ef61d
Revises: 159c77ad120c
Create Date: 2026-01-21 22:02:24.741147

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '340a297ef61d'
down_revision = '159c77ad120c'
branch_labels = None
depends_on = None


def upgrade():
    # Legacy migration superseded by e31466bfaefe_init.
    pass


def downgrade():
    # Legacy migration superseded by e31466bfaefe_init.
    pass
