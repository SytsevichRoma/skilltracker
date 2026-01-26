"""Create user table

Revision ID: 3551d279eded
Revises: 
Create Date: 2026-01-19 13:57:24.682618

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3551d279eded'
down_revision = 'e31466bfaefe'
branch_labels = None
depends_on = None


def upgrade():
    # Legacy migration superseded by e31466bfaefe_init.
    pass


def downgrade():
    # Legacy migration superseded by e31466bfaefe_init.
    pass
