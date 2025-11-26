# app/domains/notifications/router/health_router.py

from fastapi import APIRouter, Request, Header, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.notifications.health_schema import HealthFeedbackRequest
from app.domains.notifications.service.health_service import HealthService

router = APIRouter(prefix="/api/v1/notifications")


@router.post("/health")
def create_health_notification(
    request: Request,
    body: HealthFeedbackRequest,
    authorization: str = Header(None, alias="Authorization"),
    db: Session = Depends(get_db),
):
    service = HealthService(db)
    return service.generate_health_feedback(request, authorization, body)
