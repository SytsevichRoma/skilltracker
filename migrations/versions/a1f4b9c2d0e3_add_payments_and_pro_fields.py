"""Add payments and pro fields

Revision ID: a1f4b9c2d0e3
Revises: 6f4c2a0f2b3b
Create Date: 2026-01-26 19:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a1f4b9c2d0e3"
down_revision = "6f4c2a0f2b3b"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(sa.Column("is_pro", sa.Boolean(), nullable=False, server_default=sa.false()))
        batch_op.add_column(sa.Column("pro_until", sa.DateTime(), nullable=True))

    op.create_table(
        "payment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.String(length=64), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("payment", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_payment_order_id"), ["order_id"], unique=True)
        batch_op.create_index(batch_op.f("ix_payment_status"), ["status"], unique=False)
        batch_op.create_index(batch_op.f("ix_payment_user_id"), ["user_id"], unique=False)


def downgrade():
    with op.batch_alter_table("payment", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_payment_user_id"))
        batch_op.drop_index(batch_op.f("ix_payment_status"))
        batch_op.drop_index(batch_op.f("ix_payment_order_id"))

    op.drop_table("payment")

    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_column("pro_until")
        batch_op.drop_column("is_pro")
