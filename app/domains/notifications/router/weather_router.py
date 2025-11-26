# app/domains/notifications/router/weather_router.py

from fastapi import APIRouter, Request, Depends, Header
from sqlalchemy.orm import Session

from app.db import get_db
from app.domains.notifications.service.weather_service import WeatherService
from app.schemas.notifications.weather_schema import WeatherRecommendationRequest

router = APIRouter(prefix="/api/v1/notifications/weather", tags=["Weather Notification"])


# -----------------------------
# 1) 수동/즉시 API (사용자 요청)
# -----------------------------

@router.post("/recommendation")
def create_weather_recommendation(
    request: Request,
    body: WeatherRecommendationRequest,
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None)   # ← 핵심
):
    return WeatherService(db).generate_weather_recommendation(
        request=request,
        authorization=authorization,
        body=body,
    )

# -----------------------------
# 2) 자동 추천 (스케줄러 내부 호출)
# -----------------------------
@router.post("/auto/{pet_id}")
def auto_weather(pet_id: int, db: Session = Depends(get_db)):
    WeatherService(db).generate_auto_weather_for_pet(pet_id)
    return {"success": True, "pet_id": pet_id}
