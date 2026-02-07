"""Add agent_logs and agent_messages tables

Revision ID: a1b2c3d4e5f6
Revises: 098f8858ee4e
Create Date: 2026-02-07 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '098f8858ee4e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('agent_logs',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('agent_type', sa.String(), nullable=False),
        sa.Column('input_data', sa.JSON(), nullable=False),
        sa.Column('output_data', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_agent_logs_user_id', 'agent_logs', ['user_id'])

    op.create_table('agent_messages',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('agent_type', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_agent_messages_user_id', 'agent_messages', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_agent_messages_user_id', table_name='agent_messages')
    op.drop_table('agent_messages')
    op.drop_index('ix_agent_logs_user_id', table_name='agent_logs')
    op.drop_table('agent_logs')
