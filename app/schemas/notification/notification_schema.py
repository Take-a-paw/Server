from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RelatedPetSchema(BaseModel):
    pet_id: int = Field(..., description="반려동물 ID")
    name: str = Field(..., description="반려동물 이름")
    image_url: Optional[str] = Field(None, description="반려동물 이미지 URL")

    class Config:
        from_attributes = True

class RelatedUserSchema(BaseModel):
    user_id: int = Field(..., description="사용자 ID")
    nickname: str = Field(..., description="닉네임")
    profile_img_url: Optional[str] = Field(None, description="프로필 이미지 URL")

    class Config:
        from_attributes = True

class NotificationItemSchema(BaseModel):
    notification_id: int = Field(..., description="알림 ID")
    type: str = Field(..., description="알림 타입")
    title: str = Field(..., description="알림 제목")
    message: str = Field(..., description="알림 내용")

    family_id: Optional[int] = Field(None, description="가족 ID (해당되는 경우)")
    target_user_id: Optional[int] = Field(None, description="알림을 받는 유저 ID")

    related_pet: Optional[RelatedPetSchema] = Field(
        None, description="관련 반려동물 정보"
    )
    related_user: Optional[RelatedUserSchema] = Field(
        None, description="관련 사용자 정보"
    )

    related_lat: Optional[float] = Field(None, description="관련 장소 위도")
    related_lng: Optional[float] = Field(None, description="관련 장소 경도")

    is_read: bool = Field(..., description="읽음 여부")
    read_count: int = Field(..., description="해당 알림을 읽은 가족 수")
    unread_count: int = Field(..., description="아직 읽지 않은 가족 수")

    created_at: datetime = Field(..., description="알림 생성 시각")

    class Config:
        from_attributes = True

class NotificationListResponse(BaseModel):
    success: bool = Field(True, description="성공 여부")
    status: int = Field(200, description="HTTP Status Code")

    notifications: List[NotificationItemSchema] = Field(
        ..., description="알림 목록"
    )

    page: int = Field(..., description="현재 페이지 번호")
    size: int = Field(..., description="페이지 크기")
    total_count: int = Field(..., description="전체 알림 수")

    timeStamp: str = Field(..., description="응답 생성 시각 (ISO8601)")
    path: str = Field(..., description="요청 경로")
