"""initial migration with all tables

Revision ID: 135163ce471a
Revises:
Create Date: 2025-11-30 18:02:05.362312
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel

revision: str = "135163ce471a"
down_revision: Union[str, Sequence[str], None] = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create tables with fully defined enums

    op.create_table(
        "app_user",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("full_name", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("stag", sqlmodel.sql.sqltypes.AutoString(length=9), nullable=True),
        sa.Column("password_hash", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "role",
            sa.Enum(
                "USER",
                "ADMIN",
                "SUPER_ADMIN",
                "DELETED_USER",
                name="role_enum"
            ),
            nullable=False,
            server_default="USER",
        ),
        sa.Column("is_verified", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("is_enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("is_deleted", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("is_anonymized", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.Column("verification_code_expires_at", sa.DateTime(timezone=True)),
        sa.Column("last_login_at", sa.DateTime(timezone=True)),
        sa.Column("last_failed_login_at", sa.DateTime(timezone=True)),
        sa.Column("failed_login_attempts", sa.Integer(), nullable=False),
        sa.Column("verification_code", sqlmodel.sql.sqltypes.AutoString()),
        sa.Column("token_version", sa.Integer(), nullable=False),
        sa.Column(
            "preferred_currency",
            sa.Enum("EUR", "USD", "PLN", "GBP", "CAD", name="currency_enum"),
            server_default="EUR",
            nullable=False
        ),
        sa.Column("preferred_language", sqlmodel.sql.sqltypes.AutoString()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_app_user_created_at", "app_user", ["created_at"])
    op.create_index("ix_app_user_email", "app_user", ["email"], unique=True)
    op.create_index("ix_app_user_stag", "app_user", ["stag"], unique=True)

    op.create_table(
        "exchange_rate",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("is_anonymized", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("currency", sqlmodel.sql.sqltypes.AutoString()),
        sa.Column("rate_to_eur", sa.Numeric(precision=20, scale=10), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "groups",
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("target_balance", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("current_balance", sa.Numeric(precision=10, scale=2)),
        sa.Column("require_admin_approval_for_funds_removal", sa.Boolean(), nullable=False),
        sa.Column("currency", sa.Enum("EUR", "USD", "PLN", "GBP", "CAD", name="currency_enum"), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "gdpr_request",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.UUID()),
        sa.Column("user_email_snapshot", sqlmodel.sql.sqltypes.AutoString()),
        sa.Column("user_full_name_snapshot", sqlmodel.sql.sqltypes.AutoString()),
        sa.Column("request_type", sa.Enum("DATA_EXPORT", "DATA_MODIFICATION", name="gdpr_request_type_enum")),
        sa.Column(
            "status",
            sa.Enum("PROCESSING", "COMPLETED", "REFUSED", name="gdpr_request_status_enum"),
            server_default="PROCESSING",
            nullable=False,
        ),
        sa.Column("refusal_reason", sqlmodel.sql.sqltypes.AutoString()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["app_user.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_gdpr_request_created_at", "gdpr_request", ["created_at"])

    op.create_table(
        "group_member",
        sa.Column("role", sa.Enum("ADMIN", "MEMBER", name="grouprole")),
        sa.Column("contributed_amount", sa.Numeric(precision=10, scale=2)),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("group_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["app_user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "group_transaction_message",
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column(
            "type",
            sa.Enum(
                "WALLET_DEPOSIT",
                "WALLET_WITHDRAWAL",
                "GROUP_SAVINGS_DEPOSIT",
                "GROUP_SAVINGS_WITHDRAWAL",
                "INDIVIDUAL_SAVINGS_DEPOSIT",
                "INDIVIDUAL_SAVINGS_WITHDRAWAL",
                name="transactiontype",
            ),
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("group_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["app_user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "removed_group_member",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("group_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("removed_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["app_user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "wallet",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid()),
        sa.Column("is_anonymized", sa.Boolean(), server_default="false"),
        sa.Column("total_balance", sa.Numeric(precision=15, scale=4), server_default=sa.text("0"), nullable=False),
        sa.Column("locked_amount", sa.Numeric(precision=15, scale=4), server_default=sa.text("0"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["user_id"], ["app_user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_wallet_created_at", "wallet", ["created_at"])

    op.create_table(
        "transaction",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("is_anonymized", sa.Boolean(), server_default="false"),
        sa.Column("amount", sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column(
            "type",
            sa.Enum(
                "WALLET_DEPOSIT",
                "WALLET_WITHDRAWAL",
                "GROUP_SAVINGS_DEPOSIT",
                "GROUP_SAVINGS_WITHDRAWAL",
                "INDIVIDUAL_SAVINGS_DEPOSIT",
                "INDIVIDUAL_SAVINGS_WITHDRAWAL",
                name="transaction_type_enum",
            ),
            nullable=False,
        ),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString()),
        sa.Column(
            "status",
            sa.Enum("PENDING", "COMPLETED", "FAILED", name="transaction_status_enum"),
            server_default="PENDING",
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("executed_at", sa.DateTime(timezone=True)),
        sa.Column("wallet_id", sa.Uuid(), nullable=False),
        sa.Column("owner_id", sa.Uuid()),
        sa.ForeignKeyConstraint(["owner_id"], ["app_user.id"]),
        sa.ForeignKeyConstraint(["wallet_id"], ["wallet.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_transaction_created_at", "transaction", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_transaction_created_at", table_name="transaction")
    op.drop_table("transaction")

    op.drop_index("ix_wallet_created_at", table_name="wallet")
    op.drop_table("wallet")

    op.drop_table("removed_group_member")
    op.drop_table("group_transaction_message")
    op.drop_table("group_member")

    op.drop_index("ix_gdpr_request_created_at", table_name="gdpr_request")
    op.drop_table("gdpr_request")

    op.drop_table("groups")
    op.drop_table("exchange_rate")

    op.drop_index("ix_app_user_stag", table_name="app_user")
    op.drop_index("ix_app_user_email", table_name="app_user")
    op.drop_index("ix_app_user_created_at", table_name="app_user")
    op.drop_table("app_user")

    # Drop enums after all tables are gone
    enums = [
        "currency_enum",
        "role_enum",
        "gdpr_request_type_enum",
        "gdpr_request_status_enum",
        "grouprole",
        "transactiontype",
        "transaction_type_enum",
        "transaction_status_enum",
    ]
    for enum in enums:
        op.execute(f"DROP TYPE IF EXISTS {enum}")
