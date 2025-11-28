"""v1-live initial commit

Revision ID: 87156f1d8833
Revises: 
Create Date: 2025-11-28 19:57:24.984001
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '87156f1d8833'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # --- define enums ---
    role_enum = sa.Enum('USER', 'ADMIN', 'SUPER_ADMIN', 'DELETED_USER', name='role_enum')
    currency_enum = sa.Enum('EUR', 'USD', 'PLN', 'GBP', 'CAD', name='currency_enum')
    gdpr_request_status_enum = sa.Enum('PROCESSING', 'COMPLETED', 'REFUSED', name='gdpr_request_status_enum')
    gdpr_request_type_enum = sa.Enum('DATA_EXPORT', 'DATA_MODIFICATION', name='gdpr_request_type_enum')
    transaction_status_enum = sa.Enum('PENDING', 'COMPLETED', 'FAILED', name='transaction_status_enum')
    transaction_type_enum = sa.Enum(
        'WALLET_DEPOSIT',
        'WALLET_WITHDRAWAL',
        'GROUP_SAVINGS_DEPOSIT',
        'GROUP_SAVINGS_WITHDRAWAL',
        'INDIVIDUAL_SAVINGS_DEPOSIT',
        'INDIVIDUAL_SAVINGS_WITHDRAWAL',
        name='transaction_type_enum'
    )

    # --- create tables ---
    op.create_table(
        'app_user',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('email', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('full_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('stag', sqlmodel.sql.sqltypes.AutoString(length=9), nullable=True),
        sa.Column('password_hash', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('role', role_enum, server_default='USER', nullable=False),
        sa.Column('is_verified', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('is_enabled', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('is_anonymized', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verification_code_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_failed_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=False),
        sa.Column('verification_code', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('token_version', sa.Integer(), nullable=False),
        sa.Column('preferred_currency', currency_enum, server_default='EUR', nullable=False),
        sa.Column('preferred_language', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_app_user_created_at'), 'app_user', ['created_at'], unique=False)
    op.create_index(op.f('ix_app_user_email'), 'app_user', ['email'], unique=True)
    op.create_index(op.f('ix_app_user_stag'), 'app_user', ['stag'], unique=True)

    op.create_table(
        'exchange_rate',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('is_anonymized', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('currency', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('rate_to_eur', sa.Numeric(precision=20, scale=10), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'gdpr_request',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=True),
        sa.Column('user_email_snapshot', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('user_full_name_snapshot', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('request_type', gdpr_request_type_enum, nullable=True),
        sa.Column('status', gdpr_request_status_enum, server_default='PROCESSING', nullable=False),
        sa.Column('refusal_reason', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['app_user.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_gdpr_request_created_at'), 'gdpr_request', ['created_at'], unique=False)

    op.create_table(
        'wallet',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=True),
        sa.Column('is_anonymized', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('total_balance', sa.Numeric(precision=15, scale=4), server_default=sa.text('0'), nullable=False),
        sa.Column('locked_amount', sa.Numeric(precision=15, scale=4), server_default=sa.text('0'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['app_user.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_wallet_created_at'), 'wallet', ['created_at'], unique=False)

    op.create_table(
        'transaction',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('is_anonymized', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('amount', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('type', transaction_type_enum, nullable=False),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('status', transaction_status_enum, server_default='PENDING', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('executed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('wallet_id', sa.Uuid(), nullable=False),
        sa.Column('owner_id', sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['app_user.id']),
        sa.ForeignKeyConstraint(['wallet_id'], ['wallet.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transaction_created_at'), 'transaction', ['created_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""

    # drop tables respecting dependencies
    op.drop_index(op.f('ix_transaction_created_at'), table_name='transaction')
    op.drop_table('transaction')
    op.drop_index(op.f('ix_wallet_created_at'), table_name='wallet')
    op.drop_table('wallet')
    op.drop_index(op.f('ix_gdpr_request_created_at'), table_name='gdpr_request')
    op.drop_table('gdpr_request')
    op.drop_table('exchange_rate')
    op.drop_index(op.f('ix_app_user_stag'), table_name='app_user')
    op.drop_index(op.f('ix_app_user_email'), table_name='app_user')
    op.drop_index(op.f('ix_app_user_created_at'), table_name='app_user')
    op.drop_table('app_user')

    # drop enums safely
    sa.Enum(name='transaction_type_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='transaction_status_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='gdpr_request_type_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='gdpr_request_status_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='currency_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='role_enum').drop(op.get_bind(), checkfirst=True)
