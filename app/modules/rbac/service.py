# app/modules/rbac/service.py

from app.modules.rbac.repository import RBACRepository
from app.modules.rbac.schemas import AdminUserUpdate
from app.core.utils.exceptions import CustomException

class RBACService:
    def __init__(self, repo: RBACRepository):
        self.repo = repo

    async def get_all_users(self, page: int, size: int):
        skip = (page - 1) * size
        users, total = await self.repo.get_all_users(skip=skip, limit=size)
        return {
            "items": users,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }

    async def get_app_metrics(self):
        return await self.repo.get_app_metrics()

    async def update_user(self, user_id: str, update_data: AdminUserUpdate):
        user = await self.repo.get_user_by_id(user_id)
        if not user:
            raise CustomException.e404_not_found("User not found.")

        updates = update_data.model_dump(exclude_unset=True)
        
        if not updates:
            return user

        # Explicitly prevent updating restricted fields if they somehow slipped through
        # Though schema validation should handle most, this is a safety net
        restricted_fields = ['email', 'password_hash', 'id', 'created_at', 'updated_at', 
                             'deleted_at', 'last_login_at', 'last_failed_login_at', 
                             'verification_code_expires_at']
        
        for field in restricted_fields:
            if field in updates:
                del updates[field]

        return await self.repo.update_user(user, updates)
