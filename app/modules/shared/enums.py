from enum import StrEnum

class Currency(StrEnum):
    """Enumeration of supported currencies."""

    EUR = "EUR"
    USD = "USD"
    PLN = "PLN"
    GBP = "GBP"
    CAD = "CAD"

class TransactionType(StrEnum):
    """Enumeration of transaction types."""

    WALLET_DEPOSIT = "WALLET_DEPOSIT"
    WALLET_WITHDRAWAL = "WALLET_WITHDRAWAL"
    GROUP_SAVINGS_DEPOSIT = "GROUP_SAVINGS_DEPOSIT"
    GROUP_SAVINGS_WITHDRAWAL = "GROUP_SAVINGS_WITHDRAWAL"
    INDIVIDUAL_SAVINGS_DEPOSIT = "INDIVIDUAL_SAVINGS_DEPOSIT"
    INDIVIDUAL_SAVINGS_WITHDRAWAL = "INDIVIDUAL_SAVINGS_WITHDRAWAL"


class TransactionStatus(StrEnum):
    """Enumeration of transaction statuses."""

    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Role(StrEnum):
    """Enumeration of user roles with increasing privileges."""

    USER = "USER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"
