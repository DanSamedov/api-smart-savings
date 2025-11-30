# app/modules/group/schemas.py

from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field

from app.modules.shared.enums import Currency   


class GroupUpdate(BaseModel):
    """Schema for updating group details."""
    name: Optional[str] = None
    target_balance: Optional[float] = None
    require_admin_approval_for_funds_removal: Optional[bool] = None
    currency: Optional[Currency] = None
    

class AddMemberRequest(BaseModel):
    """Schema for adding a member to a group."""
    email: str


class RemoveMemberRequest(BaseModel):
    """Schema for removing a member from a group."""
    user_id: UUID


class GroupDepositRequest(BaseModel):
    """Schema for depositing funds into a group."""
    amount: float = Field(gt=0, description="Amount to deposit")


class GroupWithdrawRequest(BaseModel):
    """Schema for withdrawing funds from a group."""
    amount: float = Field(gt=0, description="Amount to withdraw")
