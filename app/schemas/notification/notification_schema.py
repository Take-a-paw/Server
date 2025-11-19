from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NotificationResponse(BaseModel):
    notification_id: int
    family_id: int
    target_user_id: int
    type: str
    title: str
    message: str
    related_pet_id: Optional[int] = None
    related_user_id: Optional[int] = None
    created_at: datetime

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "notification_id": 12,
                "family_id": 5,
                "target_user_id": 3,
                "type": "ACTIVITY_START",
                "title": "산책 시작",
                "message": "지원님이 몽이와 산책을 시작했습니다.",
                "related_pet_id": 7,
                "related_user_id": 3,
                "created_at": "2025-03-01T10:22:15Z"
            }
        }


class NotificationListResponse(BaseModel):
    success: bool
    status: int
    count: int
    notifications: List[NotificationResponse]
    timeStamp: datetime
    path: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "success": True,
                "status": 200,
                "count": 2,
                "notifications": [
                    {
                        "notification_id": 12,
                        "family_id": 5,
                        "target_user_id": 3,
                        "type": "ACTIVITY_START",
                        "title": "산책 시작",
                        "message": "지원님이 몽이와 산책을 시작했습니다.",
                        "related_pet_id": 7,
                        "related_user_id": 3,
                        "created_at": "2025-03-01T10:22:15Z"
                    },
                    {
                        "notification_id": 13,
                        "family_id": 5,
                        "target_user_id": 3,
                        "type": "REQUEST",
                        "title": "반려동물 공유 요청",
                        "message": "민서님이 몽이 공유 요청을 보냈습니다.",
                        "related_pet_id": 7,
                        "related_user_id": 10,
                        "created_at": "2025-03-02T13:41:00Z"
                    }
                ],
                "timeStamp": "2025-03-02T13:41:00Z",
                "path": "/api/v1/notifications/pets/7"
            }
        }
