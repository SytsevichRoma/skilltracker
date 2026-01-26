"""Add payment provider

Revision ID: f2c9b0b8c6a1
Revises: a1f4b9c2d0e3
Create Date: 2026-01-26 20:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f2c9b0b8c6a1"
down_revision = "a1f4b9c2d0e3"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("payment", schema=None) as batch_op:
        batch_op.add_column(sa.Column("provider", sa.String(length=16), nullable=False, server_default="fondy"))
        batch_op.create_index(batch_op.f("ix_payment_provider"), ["provider"], unique=False)


def downgrade():
    with op.batch_alter_table("payment", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_payment_provider"))
        batch_op.drop_column("provider")
