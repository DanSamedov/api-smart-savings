"""update - use DB-level timestamp for created_at and backfill null values

Revision ID: 810f5c93dc63
Revises: fc3cd89f494b
Create Date: 2025-11-28 18:56:32.062112
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '810f5c93dc63'
down_revision: Union[str, Sequence[str], None] = 'fc3cd89f494b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: add DB-level default and index for created_at"""
    # --- transaction table ---
    op.alter_column(
        'transaction',
        'created_at',
        existing_type=postgresql.TIMESTAMP(timezone=True),
        server_default=sa.text("now()"),
        nullable=False
    )
    op.create_index(op.f('ix_transaction_created_at'), 'transaction', ['created_at'], unique=False)
    op.execute("UPDATE transaction SET created_at = NOW() WHERE created_at IS NULL;")

    # --- wallet table ---
    op.alter_column(
        'wallet',
        'created_at',
        existing_type=postgresql.TIMESTAMP(timezone=True),
        server_default=sa.text("now()"),
        nullable=False
    )
    op.create_index(op.f('ix_wallet_created_at'), 'wallet', ['created_at'], unique=False)
    op.execute("UPDATE wallet SET created_at = NOW() WHERE created_at IS NULL;")

    # --- app_user table ---
    op.alter_column(
        'app_user',
        'created_at',
        existing_type=postgresql.TIMESTAMP(timezone=True),
        server_default=sa.text("now()"),
        nullable=False
    )
    op.create_index(op.f('ix_app_user_created_at'), 'app_user', ['created_at'], unique=False)
    op.execute("UPDATE app_user SET created_at = NOW() WHERE created_at IS NULL;")

    # --- gdpr_request table ---
    op.alter_column(
        'gdpr_request',
        'created_at',
        existing_type=postgresql.TIMESTAMP(timezone=True),
        server_default=sa.text("now()"),
        nullable=False
    )
    op.create_index(op.f('ix_gdpr_request_created_at'), 'gdpr_request', ['created_at'], unique=False)
    op.execute("UPDATE gdpr_request SET created_at = NOW() WHERE created_at IS NULL;")


def downgrade() -> None:
    """Downgrade schema: remove DB defaults and indexes"""
    # --- transaction table ---
    op.drop_index(op.f('ix_transaction_created_at'), table_name='transaction')
    op.alter_column(
        'transaction',
        'created_at',
        existing_type=postgresql.TIMESTAMP(timezone=True),
        server_default=None,
        nullable=True
    )

    # --- wallet table ---
    op.drop_index(op.f('ix_wallet_created_at'), table_name='wallet')
    op.alter_column(
        'wallet',
        'created_at',
        existing_type=postgresql.TIMESTAMP(timezone=True),
        server_default=None,
        nullable=True
    )

    # --- app_user table ---
    op.drop_index(op.f('ix_app_user_created_at'), table_name='app_user')
    op.alter_column(
        'app_user',
        'created_at',
        existing_type=postgresql.TIMESTAMP(timezone=True),
        server_default=None,
        nullable=True
    )

    # --- gdpr_request table ---
    op.drop_index(op.f('ix_gdpr_request_created_at'), table_name='gdpr_request')
    op.alter_column(
        'gdpr_request',
        'created_at',
        existing_type=postgresql.TIMESTAMP(timezone=True),
        server_default=None,
        nullable=True
    )
