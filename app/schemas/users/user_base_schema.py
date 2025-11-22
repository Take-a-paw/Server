# app/schemas/users/user_base_schema.py

from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    user_id: int
    firebase_uid: str
    nickname: str
    email: Optional[str]
    phone: Optional[str]
    profile_img_url: Optional[str]
    sns: str
    created_at: str
    updated_at: Optional[str]

    class Config:
        from_attributes = True  # ORM -> Pydantic 자동 변환
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "firebase_uid": "fba_2903jf923",
                "nickname": "지환",
                "email": "example@test.com",
                "phone": "010-1234-5678",
                "profile_img_url": "https://.../profile.png",
                "sns": "kakao",
                "created_at": "2025-11-22T12:33:22",
                "updated_at": "2025-11-22T13:12:11"
            }
        }
