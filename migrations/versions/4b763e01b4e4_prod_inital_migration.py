"""prod initial migration - inline enums

Revision ID: 000000000002
Revises: 
Create Date: 2025-12-01 23:55:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "000000000002"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Create tables with inline enums ---
    op.create_table(
        "app_user",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(), nullable=False, unique=True, index=True),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column("stag", sa.String(9), nullable=True, unique=True, index=True),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column(
            "role",
            sa.Enum("USER", "ADMIN", "SUPER_ADMIN", "DELETED_USER", name="role_enum"),
            nullable=False,
            server_default="USER",
        ),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_anonymized", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.Column("verification_code_expires_at", sa.DateTime(timezone=True)),
        sa.Column("last_login_at", sa.DateTime(timezone=True)),
        sa.Column("last_failed_login_at", sa.DateTime(timezone=True)),
        sa.Column("failed_login_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("verification_code", sa.String(), nullable=True),
        sa.Column("token_version", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "preferred_currency",
            sa.Enum("EUR", "USD", "PLN", "GBP", name="currency_enum"),
            nullable=False,
            server_default="EUR",
        ),
        sa.Column("preferred_language", sa.String(), nullable=True),
    )

    op.create_table(
        "wallet",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("app_user.id"), unique=True),
        sa.Column("is_anonymized", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("total_balance", sa.Numeric(15,4), nullable=False, server_default="0"),
        sa.Column("locked_amount", sa.Numeric(15,4), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "groups",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("target_balance", sa.Numeric(10,2), nullable=False),
        sa.Column("current_balance", sa.Numeric(10,2), nullable=False, server_default="0"),
        sa.Column("require_admin_approval_for_funds_removal", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "currency",
            sa.Enum("EUR", "USD", "PLN", "GBP", name="currency_enum"),
            nullable=False,
            server_default="EUR",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "group_member",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("groups.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("app_user.id"), nullable=False),
        sa.Column(
            "role",
            sa.Enum("ADMIN", "MEMBER", name="group_role_enum"),
            nullable=False,
            server_default="MEMBER",
        ),
        sa.Column("contributed_amount", sa.Numeric(10,2), nullable=False, server_default="0"),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "group_transaction_message",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("groups.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("app_user.id"), nullable=False),
        sa.Column("amount", sa.Numeric(10,2), nullable=False),
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
            server_default="GROUP_SAVINGS_DEPOSIT",
        ),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "transaction",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("wallet_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("wallet.id"), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("app_user.id"), nullable=True),
        sa.Column("is_anonymized", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("amount", sa.Numeric(15,4), nullable=False),
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
        sa.Column(
            "status",
            sa.Enum("PENDING", "COMPLETED", "FAILED", name="transaction_status_enum"),
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("now()")),
    )

    op.create_table(
        "gdpr_request",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("app_user.id", ondelete="SET NULL"), nullable=True),
        sa.Column("user_email_snapshot", sa.String(), nullable=True),
        sa.Column("user_full_name_snapshot", sa.String(), nullable=True),
        sa.Column(
            "request_type",
            sa.Enum("DATA_EXPORT", "DATA_MODIFICATION", name="gdpr_request_type_enum"),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.Enum("PROCESSING", "COMPLETED", "REFUSED", name="gdpr_request_status_enum"),
            nullable=False,
            server_default="PROCESSING",
        ),
        sa.Column("refusal_reason", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("now()")),
    )

    op.create_table(
        "removed_group_member",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("groups.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("app_user.id"), nullable=False),
        sa.Column("removed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "exchange_rate",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("is_anonymized", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("currency", sa.String(), nullable=True),
        sa.Column("rate_to_eur", sa.Numeric(20,10), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("exchange_rate")
    op.drop_table("removed_group_member")
    op.drop_table("gdpr_request")
    op.drop_table("transaction")
    op.drop_table("group_transaction_message")
    op.drop_table("group_member")
    op.drop_table("groups")
    op.drop_table("wallet")
    op.drop_table("app_user")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS currency_enum")
    op.execute("DROP TYPE IF EXISTS transaction_type_enum")
    op.execute("DROP TYPE IF EXISTS transaction_status_enum")
    op.execute("DROP TYPE IF EXISTS role_enum")
    op.execute("DROP TYPE IF EXISTS group_role_enum")
    op.execute("DROP TYPE IF EXISTS gdpr_request_type_enum")
    op.execute("DROP TYPE IF EXISTS gdpr_request_status_enum")
