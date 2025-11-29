from pydantic import BaseModel, Field
from typing import Optional


class WalkRecommendationRequest(BaseModel):
    pet_id: int = Field(..., description="반려동물 ID")
    lat: float = Field(..., description="현재 위치 위도")
    lng: float = Field(..., description="현재 위치 경도")
    weather_status: Optional[str] = Field(None, description="날씨 상태 (예: '맑음', '흐림', '비' 등)")
    weather_temp_c: Optional[float] = Field(None, description="현재 온도 (섭씨)")
    today_walk_count: Optional[int] = Field(None, description="오늘 산책 횟수")
    today_total_distance_km: Optional[float] = Field(None, description="오늘 총 산책 거리 (km)")

