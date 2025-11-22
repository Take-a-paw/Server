# app/schemas/users/user_update_schema.py

from pydantic import BaseModel
from typing import Optional


class UserUpdateRequest(BaseModel):
    nickname: Optional[str] = None
    phone: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "nickname": "새 닉네임",
                "phone": "010-9999-9999"
            }
        }
