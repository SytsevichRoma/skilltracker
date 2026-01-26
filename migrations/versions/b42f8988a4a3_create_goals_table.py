"""Create goals table

Revision ID: b42f8988a4a3
Revises: 3551d279eded
Create Date: 2026-01-21 21:16:18.559353

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b42f8988a4a3'
down_revision = '3551d279eded'
branch_labels = None
depends_on = None


def upgrade():
    # Legacy migration superseded by e31466bfaefe_init.
    pass


def downgrade():
    # Legacy migration superseded by e31466bfaefe_init.
    pass
