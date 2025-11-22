# app/routers/notifications.py
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db import get_db
from app.domains.notifications.service.notification_service import NotificationService
from app.schemas.notifications.notification_schema import NotificationListResponse

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])


@router.get(
    "/pet/{pet_id}",
    summary="특정 반려동물 알림 리스트 조회",
    response_model=NotificationListResponse
)
def get_notifications_by_pet(pet_id: int, request: Request, db: Session = Depends(get_db)):
    service = NotificationService(db)
    return service.get_by_pet(pet_id, request)


@router.patch(
    "/{notification_id}/read",
    summary="알림 읽음 처리",
    description="알림을 읽음 처리합니다."
)
def mark_notification_as_read(notification_id: int, request: Request, db: Session = Depends(get_db)):
    service = NotificationService(db)
    return service.mark_read(notification_id, request)
