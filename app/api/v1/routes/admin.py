from fastapi import APIRouter, Depends, Query

from app.api.dependencies import (get_current_admin_user,
                                  get_current_super_admin_user,
                                  get_rbac_service)
from app.core.utils.response import AppMetricsResponse, PaginatedUsersResponse
from app.modules.rbac.schemas import AdminUserUpdate
from app.modules.rbac.service import RBACService
from app.modules.user.models import User
from app.modules.user.schemas import UserResponse

router = APIRouter()


@router.get("/users/all", response_model=PaginatedUsersResponse)
async def get_all_users(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    service: RBACService = Depends(get_rbac_service),
    _: User = Depends(get_current_admin_user),
):
    """
    Retrieve a paginated list of all users in the system.

    Restricted to users with ADMIN or SUPER_ADMIN roles.
    It returns user details including status, login history, and role.
    """
    data = await service.get_all_users(page, size)
    return PaginatedUsersResponse(data=data, message="Users retrieved successfully.")


@router.get("/app-metrics", response_model=AppMetricsResponse)
async def get_app_metrics(
    service: RBACService = Depends(get_rbac_service),
    _: User = Depends(get_current_admin_user),
):
    """
    Retrieve application-wide metrics.

    Restricted to users with ADMIN or SUPER_ADMIN roles.
    It returns the total number of transactions, the sum of all wallet balances,
    and the total number of registered users.
    """
    data = await service.get_app_metrics()
    return AppMetricsResponse(data=data, message="App metrics retrieved successfully.")


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    update_data: AdminUserUpdate,
    service: RBACService = Depends(get_rbac_service),
    _: User = Depends(get_current_super_admin_user),
):
    """
    Update a specific user's details.

    Restricted to SUPER_ADMIN role only.
    Allowed updates: role, is_enabled, is_verified.
    """
    updated_user = await service.update_user(user_id, update_data)
    return updated_user
