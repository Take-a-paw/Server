from fastapi import APIRouter, Depends, Request, Header
from sqlalchemy.orm import Session

from app.db import get_db
from app.domains.notifications.service.notification_service import NotificationService
from app.schemas.notifications.notification_schema import NotificationListResponse, NotificationErrorResponse


router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])


@router.get(
    "",
    summary="알림 리스트 조회",
    description="선택된 pet_id, type, 페이지네이션 기준으로 알림 목록을 조회합니다.",
    response_model=NotificationListResponse,
    responses={
        400: {"model": NotificationErrorResponse},
        401: {"model": NotificationErrorResponse},
        404: {"model": NotificationErrorResponse},
        500: {"model": NotificationErrorResponse},
    }
)
def get_notifications(
    request: Request,
    pet_id: int | None = None,
    type: str | None = None,
    page: int = 0,
    size: int = 20,
    authorization: str | None = Header(None),
    db: Session = Depends(get_db),
):
    firebase_token = None
    if authorization and authorization.startswith("Bearer "):
        firebase_token = authorization.split(" ")[1]

    service = NotificationService(db)
    return service.get_notifications(
        request=request,
        firebase_token=firebase_token,
        pet_id=pet_id,
        notif_type=type,
        page=page,
        size=size
    )
