# app/modules/rbac/repository.py

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.user.models import User
from app.modules.wallet.models import Transaction, Wallet


class RBACRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_users(self, skip: int, limit: int):
        query = select(User).offset(skip).limit(limit)
        result = await self.session.execute(query)
        users = result.scalars().all()

        count_query = select(func.count(User.id))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        return users, total

    async def get_app_metrics(self):
        trans_count_query = select(func.count(Transaction.id))
        trans_count = (await self.session.execute(trans_count_query)).scalar() or 0

        balance_sum_query = select(func.sum(Wallet.total_balance))
        balance_sum = (await self.session.execute(balance_sum_query)).scalar() or 0

        user_count_query = select(func.count(User.id))
        user_count = (await self.session.execute(user_count_query)).scalar() or 0

        return {
            "transaction_count": trans_count,
            "total_balance_sum": balance_sum,
            "user_count": user_count,
        }

    async def get_user_by_id(self, user_id: str):
        query = select(User).where(User.id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_user(self, user: User, updates: dict):
        for key, value in updates.items():
            setattr(user, key, value)
        await self.session.commit()
        await self.session.refresh(user)
        return user
