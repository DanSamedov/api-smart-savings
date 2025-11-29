# app/modules/rbac/service.py

from app.modules.rbac.repository import RBACRepository

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
