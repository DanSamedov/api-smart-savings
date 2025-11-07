# app/modules/wallet/models.py

from datetime import datetime, timezone
from enum import StrEnum
from typing import Optional, TYPE_CHECKING

from pydantic import EmailStr
from sqlalchemy import Column, DateTime, func, Numeric, CheckConstraint
from sqlmodel import Boolean, Field, SQLModel, Relationship
from app.modules.shared.enums import Currency, TransactionType, TransactionStatus

if TYPE_CHECKING:
    from app.modules.user.models import User


class Wallet(SQLModel, table=True):
    """
    Wallet model representing user wallets with currency and balance.
    Relationships:
    - user_id: one-to-one relationship with User model.
    """

    __tablename__ = "wallet"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="wallet")
    balance: float = Field(sa_column=Column(Numeric(15, 4), nullable=False))

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        )
    )

    transactions: list["Transaction"] = Relationship(back_populates="wallet")

class ExchangeRate(SQLModel, table=True):
    """Exchange rate model for currency conversion rates."""

    __tablename__ = "exchange_rate"

    id: Optional[int] = Field(default=None, primary_key=True)
    currency: Currency = Field(index=True)
    rate_to_eur: float = Field(sa_column=Column(Numeric(20, 10), nullable=False))

    updated_at: Optional[datetime] = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        )
    )

class Transaction(SQLModel, table=True):
    """
    Transaction model representing wallet transactions.
    Relationships:
    - wallet_id : one wallet to many transactions
    - user_id : one user to many transactions
    to-do:
    - group_id : one group to many transactions
    - goal_id : one goal to many transactions
    """

    __tablename__ = "transaction"

    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float = Field(sa_column=Column(Numeric(15, 4), nullable=False))
    type: TransactionType = Field(index=True)
    description: Optional[str] = None
    status: TransactionStatus = Field(default=TransactionStatus.PENDING)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    executed_at: Optional[datetime] = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        )
    )

    wallet_id: int = Field(foreign_key="wallet.id", nullable=False)
    wallet: "Wallet" = Relationship(back_populates="transactions")

    user_id: int = Field(foreign_key="user.id", nullable=False)
    user: "User" = Relationship(back_populates="transactions")

    __table_args__ = (
        CheckConstraint(
            """
            (
                type IN ('WALLET_DEPOSIT', 'WALLET_WITHDRAWAL') AND goal_id IS NULL AND group_id IS NULL
            ) OR (
                type IN ('GOAL_SAVINGS_DEPOSIT', 'GOAL_SAVINGS_WITHDRAWAL') AND goal_id IS NOT NULL AND group_id IS NULL
            ) OR (
                type IN ('GROUP_SAVINGS_DEPOSIT', 'GROUP_SAVINGS_WITHDRAWAL') AND group_id IS NOT NULL AND goal_id IS NULL
            )
            """,
            name="check_transaction_type_fields"
        ),
    )
