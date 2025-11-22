# app/schemas/users/user_response_schema.py

from pydantic import BaseModel
from app.schemas.users.user_base_schema import UserBase


class UserMeResponse(BaseModel):
    success: bool
    status: int
    user: UserBase

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "status": 200,
                "user": UserBase.Config.json_schema_extra.get("example")
            }
        }
