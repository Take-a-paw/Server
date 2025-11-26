# app/schemas/notifications/weather_schema.py

from pydantic import BaseModel, Field, field_validator
from typing import Optional


class WeatherRecommendationRequest(BaseModel):
    pet_id: int = Field(..., description="반려동물 ID")
    trigger_type: str = Field(..., description="'manual' 또는 'scheduled'")
    lat: Optional[float] = None
    lng: Optional[float] = None

    # -------------------------
    # Pydantic v2 validators
    # -------------------------
    @field_validator("lat")
    def validate_lat(cls, v, info):
        trigger = info.data.get("trigger_type")
        if trigger == "manual" and v is None:
            raise ValueError("manual 요청일 때 lat는 필수입니다.")
        return v

    @field_validator("lng")
    def validate_lng(cls, v, info):
        trigger = info.data.get("trigger_type")
        if trigger == "manual" and v is None:
            raise ValueError("manual 요청일 때 lng는 필수입니다.")
        return v
