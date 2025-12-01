# app/modules/group/helpers.py

import uuid
from decimal import Decimal
from typing import List

from app.core.utils.exceptions import CustomException
from app.modules.group.models import Group, GroupMember
from app.modules.user.models import User


async def validate_group_exists(group: Group | None) -> None:
    """Validate that a group exists."""
    if not group:
        raise CustomException.not_found(detail="Group not found")


async def validate_user_is_member(members: List[GroupMember], user_id: uuid.UUID) -> GroupMember:
    """
    Validate that a user is a member of the group.
    
    Returns:
        GroupMember: The member object if found
        
    Raises:
        CustomException: If user is not a member
    """
    member = next((m for m in members if str(m.user_id) == str(user_id)), None)
    if not member:
        raise CustomException.forbidden(detail="Not a member of this group")
    return member


async def validate_minimum_members(members: List[GroupMember], minimum: int = 2) -> None:
    """Validate that a group has the minimum required members."""
    if len(members) < minimum:
        raise CustomException.bad_request(
            detail=f"At least {minimum} members are required before a group can accept contributions."
        )


async def validate_target_balance_not_reached(group: Group) -> None:
    """Validate that the group has not reached its target balance."""
    if group.current_balance >= group.target_balance:
        raise CustomException.bad_request(
            detail=f"Group has already reached its target balance of {group.target_balance}"
        )


async def validate_wallet_exists(wallet) -> None:
    """Validate that a wallet exists."""
    if not wallet:
        raise CustomException.not_found(detail="User wallet not found")


async def validate_positive_amount(amount: Decimal, operation: str = "Amount") -> None:
    """Validate that an amount is positive."""
    if amount <= 0:
        raise CustomException.bad_request(detail=f"{operation} must be positive")


async def validate_sufficient_wallet_balance(wallet, amount: Decimal) -> None:
    """Validate that wallet has sufficient available balance."""
    if wallet.available_balance < amount:
        raise CustomException.bad_request(detail="Insufficient funds")


async def validate_sufficient_group_balance(group: Group, amount: Decimal) -> None:
    """Validate that group has sufficient balance."""
    if group.current_balance < amount:
        raise CustomException.bad_request(detail="Insufficient funds in the group")


async def validate_withdrawal_amount(member: GroupMember, amount: Decimal) -> None:
    """Validate that withdrawal amount doesn't exceed contributed amount."""
    if member.contributed_amount < amount:
        raise CustomException.bad_request(
            detail=f"Cannot withdraw more than contributed amount ({member.contributed_amount})"
        )


def calculate_milestone_percentage(current_balance: Decimal, target_balance: Decimal) -> int:
    """
    Calculate the milestone percentage reached.
    
    Returns:
        int: The milestone percentage (0, 50, or 100)
    """
    if target_balance == 0:
        return 0
    
    percentage = (current_balance / target_balance) * 100
    
    if percentage >= 100:
        return 100
    elif percentage >= 50:
        return 50
    else:
        return 0


def format_currency_amount(amount: float | Decimal) -> str:
    """Format a currency amount, removing trailing zeros."""
    return f"{float(amount):,.2f}".rstrip('0').rstrip('.')
