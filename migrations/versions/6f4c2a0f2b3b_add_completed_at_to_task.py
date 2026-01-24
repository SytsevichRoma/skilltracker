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
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.add_column(sa.Column('completed_at', sa.DateTime(), nullable=True))
        batch_op.create_index(batch_op.f('ix_task_completed_at'), ['completed_at'], unique=False)


def downgrade():
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_task_completed_at'))
        batch_op.drop_column('completed_at')
