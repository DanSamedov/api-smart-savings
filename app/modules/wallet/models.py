# app/modules/wallet/models.py

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4, UUID

from sqlalchemy import Column, DateTime, func, Numeric, CheckConstraint, Enum as SQLEnum, text
from sqlmodel import Field, SQLModel, Relationship, Boolean
from app.modules.shared.enums import TransactionType, TransactionStatus

class Wallet(SQLModel, table=True):
    """
    Wallet model representing user wallets with currency and balance.
    Relationships:
    - user_id: one-to-one relationship with a User model.
    """
    __tablename__ = "wallet"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: Optional[UUID] = Field(default=None, foreign_key="app_user.id", unique=True)
    user: "User" = Relationship(back_populates="wallet")
    is_anonymized: bool = Field(sa_column=Column(Boolean, server_default="false"))

    total_balance: float = Field(default=0, sa_column=Column(Numeric(15, 4), nullable=False, server_default=text("0")))
    locked_amount: float = Field(default=0, sa_column=Column(Numeric(15, 4), nullable=False, server_default=text("0")))

    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
            index=True
        )
    )


    updated_at: Optional[datetime] = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        )
    )

    transactions: list["Transaction"] = Relationship(back_populates="wallet")

    @property
    def available_balance(self) -> float:
        return float(self.total_balance) - float(self.locked_amount)


class ExchangeRate(SQLModel, table=True):
    """Exchange rate model for currency conversion rates."""
    __tablename__ = "exchange_rate"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    is_anonymized: bool = Field(sa_column=Column(Boolean, nullable=False, server_default="false")) # On user delete, set to True and remove user_id associations

    currency: Optional[str] = Field(default=None)
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
    TODO:
    - group_id : one group to many transactions
    - goal_id : one goal to many transactions
    """
    __tablename__ = "transaction"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    is_anonymized: bool = Field(sa_column=Column(Boolean, server_default="false"))

    amount: float = Field(sa_column=Column(Numeric(15, 4), nullable=False))
    type: TransactionType = Field(sa_column=Column(SQLEnum(TransactionType, name="transaction_type_enum"), nullable=False))
    description: Optional[str] = None
    status: TransactionStatus = Field(sa_column=Column(SQLEnum(TransactionStatus, name="transaction_status_enum"), nullable=False, server_default=TransactionStatus.PENDING.value))
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
            index=True
        )
    )

    executed_at: Optional[datetime] = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        )
    )

    wallet_id: UUID = Field(foreign_key="wallet.id", nullable=False)
    wallet: "Wallet" = Relationship(back_populates="transactions")

    owner_id: Optional[UUID] = Field(default=None, foreign_key="app_user.id")
    owner: "User" = Relationship(back_populates="transactions")

from app.modules.user.models import User

Wallet.model_rebuild()
Transaction.model_rebuild()