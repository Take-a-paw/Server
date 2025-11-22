# app/schemas/notifications/notification_schema.py

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field
from app.schemas.error_schema import ErrorResponse


# -------------------------
#  관련 서브 객체들
# -------------------------
class RelatedPetSchema(BaseModel):
    pet_id: int
    name: str
    image_url: Optional[str] = None

    class Config:
        from_attributes = True


class RelatedUserSchema(BaseModel):
    user_id: int
    nickname: str
    profile_img_url: Optional[str] = None

    class Config:
        from_attributes = True


# -------------------------
#  단일 알림 스키마
# -------------------------
class NotificationItemSchema(BaseModel):
    notification_id: int = Field(..., description="알림 ID")
    type: str = Field(..., description="알림 타입(enum 문자열)")
    title: str = Field(..., description="알림 제목")
    message: str = Field(..., description="알림 내용")

    family_id: Optional[int] = None
    target_user_id: Optional[int] = None

    related_pet: Optional[RelatedPetSchema] = None
    related_user: Optional[RelatedUserSchema] = None

    related_lat: Optional[float] = None
    related_lng: Optional[float] = None

    # ⭐ 추가됨: PetShareRequest와 연결됨
    share_request_id: Optional[int] = Field(
        None, description="수락/거절이 필요한 경우 관련된 PetShareRequest ID"
    )

    # 읽음 여부 (현재 사용자 기준)
    is_read_by_me: bool = Field(
        ..., description="현재 사용자가 해당 알림을 읽었는지 여부"
    )

    read_count: int = Field(..., description="해당 알림을 읽은 가족 수")
    unread_count: int = Field(..., description="아직 읽지 않은 가족 수")

    created_at: datetime = Field(..., description="알림 생성 시각")

    # ---- UI용 필드 ----
    display_type_label: str = Field(..., description="예: [승인 요청]")
    display_time: str = Field(..., description="'HH:MM' 형식의 표시 시간")
    display_read_text: str = Field(..., description="예: '3명 읽음'")

    sender_profile_img_url: Optional[str] = None
    sender_nickname: Optional[str] = None

    # 내가 보낸 알림인지 여부
    is_me: bool = Field(
        ..., description="현재 사용자가 보낸 알림인지 여부 (채팅 말풍선 방향)"
    )

    class Config:
        from_attributes = True


# -------------------------
#  리스트 응답
# -------------------------
class NotificationListResponse(BaseModel):
    success: bool = True
    status: int = 200

    notifications: List[NotificationItemSchema]

    page: int
    size: int
    total_count: int

    timeStamp: str
    path: str
