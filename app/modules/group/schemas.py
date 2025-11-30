# app/modules/group/schemas.py

from uuid import UUID
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

from app.modules.group.models import GroupBase, GroupMemberBase, GroupTransactionMessageBase
from app.modules.shared.enums import GroupRole, Currency


class GroupCreate(GroupBase):
    """Schema for creating a new group."""
    current_balance: Optional[float] = 0.0


class GroupUpdate(BaseModel):
    """Schema for updating group details."""
    name: Optional[str] = None
    target_balance: Optional[float] = None
    require_admin_approval_for_funds_removal: Optional[bool] = None
    currency: Optional[Currency] = None


class GroupMemberResponse(GroupMemberBase):
    """Schema for group member response."""
    id: UUID
    group_id: UUID
    user_id: UUID
    joined_at: datetime
    user_email: Optional[str] = None # Enriched field
    user_full_name: Optional[str] = None # Enriched field

    model_config = ConfigDict(from_attributes=True)


class GroupTransactionMessageResponse(GroupTransactionMessageBase):
    """Schema for group transaction message response."""
    id: UUID
    group_id: UUID
    user_id: UUID
    timestamp: datetime
    user_email: Optional[str] = None # Enriched field

    model_config = ConfigDict(from_attributes=True)


class GroupResponse(GroupBase):
    """Schema for group response."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    members: List[GroupMemberResponse] = []
    
    # Computed fields or additional info can be added here
    is_member: Optional[bool] = False
    user_role: Optional[GroupRole] = None

    model_config = ConfigDict(from_attributes=True)


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
