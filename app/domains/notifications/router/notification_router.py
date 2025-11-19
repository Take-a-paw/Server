from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.schemas.notifications.notification_schema import (
    NotificationListResponse,
)
from app.domain.notifications.service.notification_service import NotificationService


router = APIRouter(
    prefix="/api/v1/notifications",
    tags=["Notification"]
)


# ---------------------------------------------------------
# ✔ 특정 반려동물에 대한 알림 리스트 조회
# ---------------------------------------------------------
@router.get(
    "/pets/{pet_id}",
    response_model=NotificationListResponse,
    summary="특정 반려동물 알림 리스트 조회",
    description="해당 반려동물과 관련된 알림 목록을 반환합니다.",
)
def get_notifications_for_pet(
    request: Request,
    pet_id: int,
    authorization: Optional[str] = None,
    db: Session = Depends(get_db),
):
    service = NotificationService(db)
    return service.get_pet_notifications(
        request=request,
        authorization=authorization,
        pet_id=pet_id
    )
