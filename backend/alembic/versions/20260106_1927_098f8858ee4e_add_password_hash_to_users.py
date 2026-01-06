"""add_password_hash_to_users

Revision ID: 098f8858ee4e
Revises: 974cd85fc5f5
Create Date: 2026-01-06 19:27:28.982287

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '098f8858ee4e'
down_revision = '974cd85fc5f5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add password_hash column to users table
    op.add_column('users', sa.Column('password_hash', sa.String(), nullable=False, server_default=''))

    # Remove server default after column is created
    op.alter_column('users', 'password_hash', server_default=None)


def downgrade() -> None:
    # Remove password_hash column from users table
    op.drop_column('users', 'password_hash')
