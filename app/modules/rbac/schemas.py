from typing import Optional
from pydantic import BaseModel, Field

from app.modules.shared.enums import Role

class AdminUserUpdate(BaseModel):
    role: Optional[Role] = None
    is_enabled: Optional[bool] = None
    is_verified: Optional[bool] = None
