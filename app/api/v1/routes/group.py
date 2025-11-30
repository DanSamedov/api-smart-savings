# app/api/v1/routes/group.py

import uuid
from fastapi import APIRouter, Depends, status, BackgroundTasks
from fastapi.encoders import jsonable_encoder

from app.api.dependencies import get_current_user, get_group_service
from app.core.utils.response import GroupResponse, UserGroupsResponse
from app.modules.group.schemas import (
    AddMemberRequest,
    RemoveMemberRequest,
    GroupUpdate,
    GroupDepositRequest,
    GroupWithdrawRequest,
)
from app.modules.group.models import GroupBase
from app.modules.user.models import User
from app.modules.group.service import GroupService
from app.modules.shared.enums import GroupRole


router = APIRouter()

@router.post("/", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_in: GroupBase,
    service: GroupService = Depends(get_group_service),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new savings group. The user creating the group becomes its admin.
    """
    new_group = await service.create_group(group_in, current_user)

    # 1. Convert the Group object to a dictionary
    group_dict = jsonable_encoder(new_group)
    
    # 2. Add the missing computed fields
    group_dict.update({
        "members": [],
        "is_member": True,
        "user_role": GroupRole.ADMIN.value
    })
    
    return GroupResponse(data=group_dict)


@router.get("/", response_model=UserGroupsResponse, status_code=status.HTTP_200_OK)
async def get_user_groups(
    service: GroupService = Depends(get_group_service),
    current_user: User = Depends(get_current_user),
):
    """
    Get all groups the current user is a member of.
    """
    groups = await service.get_user_groups(current_user)
    return UserGroupsResponse(data=jsonable_encoder(groups))


@router.get("/{group_id}", response_model=GroupResponse, status_code=status.HTTP_200_OK)
async def get_group(
    group_id: uuid.UUID,
    service: GroupService = Depends(get_group_service),
    current_user: User = Depends(get_current_user),
):
    """
    Get detailed information about a specific group. Only members can view group details.
    """
    group = await service.get_group(group_id, current_user)
    
    # Convert to dict and enrich
    group_dict = jsonable_encoder(group)
    
    # Get member info for the current user
    current_member = next((m for m in group.members if str(m.user_id) == str(current_user.id)), None)
    
    group_dict.update({
        "is_member": True,
        "user_role": current_member.role if current_member else None,
        # Ensure members are also serialized correctly if they are objects
        "members": [jsonable_encoder(m) for m in group.members]
    })
    
    return GroupResponse(data=group_dict)


@router.patch("/{group_id}/settings", response_model=GroupResponse, status_code=status.HTTP_200_OK)
async def update_group_settings(
    group_id: uuid.UUID,
    group_in: GroupUpdate,
    service: GroupService = Depends(get_group_service),
    current_user: User = Depends(get_current_user),
):
    """
    Update a group's settings. Only the group admin can perform this action.
    """
    updated_group = await service.update_group_settings(group_id, group_in, current_user)
    
    # Convert to dict
    group_dict = jsonable_encoder(updated_group)
    
    # Since only admin can update, we know the role
    group_dict.update({
        "is_member": True,
        "user_role": GroupRole.ADMIN.value,
        "members": []
    })
    
    return GroupResponse(data=group_dict)


@router.delete("/{group_id}", status_code=status.HTTP_200_OK)
async def delete_group(
    group_id: uuid.UUID,
    service: GroupService = Depends(get_group_service),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a group. Only the group admin can perform this action.
    """
    return await service.delete_group(group_id, current_user)


@router.post("/{group_id}/add-member", status_code=status.HTTP_201_CREATED)
async def add_group_member(
    group_id: uuid.UUID,
    member_in: AddMemberRequest,
    background_tasks: BackgroundTasks = None,
    service: GroupService = Depends(get_group_service),
    current_user: User = Depends(get_current_user),
):
    """
    Add a member to a group. Only the group admin can perform this action.
    """
    return await service.add_group_member(group_id, member_in, current_user, background_tasks)


@router.post("/{group_id}/remove-member", status_code=status.HTTP_200_OK)
async def remove_group_member(
    group_id: uuid.UUID,
    member_in: RemoveMemberRequest,
    background_tasks: BackgroundTasks = None,
    service: GroupService = Depends(get_group_service),
    current_user: User = Depends(get_current_user),
):
    """
    Remove a member from a group. Only the group admin can perform this action.
    The admin cannot remove themselves.
    """
    return await service.remove_group_member(group_id, member_in, current_user, background_tasks)


@router.post("/{group_id}/contribute", status_code=status.HTTP_201_CREATED)
async def contribute_to_group(
    group_id: uuid.UUID,
    transaction_in: GroupDepositRequest,
    background_tasks: BackgroundTasks = None,
    service: GroupService = Depends(get_group_service),
    current_user: User = Depends(get_current_user),
):
    """
    Contribute funds to a group. This action is atomic and will either
    debit the user's wallet and credit the group, or fail without
    changing any balances.
    """
    return await service.contribute_to_group(group_id, transaction_in, current_user, background_tasks)


@router.post(
    "/{group_id}/remove-contribution",
    status_code=status.HTTP_201_CREATED,
)
async def remove_contribution(
    group_id: uuid.UUID,
    transaction_in: GroupWithdrawRequest,
    background_tasks: BackgroundTasks = None,
    service: GroupService = Depends(get_group_service),
    current_user: User = Depends(get_current_user),
):
    """
    Withdraw funds from a group. This action is atomic and will either
    credit the user's wallet and debit the group, or fail without
    changing any balances.
    """
    return await service.remove_contribution(group_id, transaction_in, current_user, background_tasks)
