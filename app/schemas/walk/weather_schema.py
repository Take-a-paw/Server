from pydantic import BaseModel, Field
from typing import Optional


class WeatherDetail(BaseModel):
    """날씨 상세 정보"""
    lat: float = Field(..., description="위도")
    lng: float = Field(..., description="경도")
    condition: str = Field(..., description="날씨 조건 (영문)")
    condition_ko: str = Field(..., description="날씨 조건 (한글)")
    icon: str = Field(..., description="날씨 아이콘")
    temperature_c: float = Field(..., description="온도 (℃)")
    feels_like_c: Optional[float] = Field(None, description="체감 온도 (℃)")
    humidity: Optional[int] = Field(None, description="습도 (%)")
    wind_speed_ms: Optional[float] = Field(None, description="풍속 (m/s)")
    uvi: Optional[float] = Field(None, description="자외선 지수")
    source: str = Field(..., description="데이터 소스")
    fetched_at: str = Field(..., description="조회 시간 (ISO 형식)")
    cache_age_seconds: Optional[int] = Field(None, description="캐시 나이 (초)")
    is_stale: bool = Field(False, description="캐시가 오래되었는지 여부")


class WeatherResponse(BaseModel):
    """날씨 정보 조회 응답"""
    success: bool = Field(True, description="성공 여부")
    status: int = Field(200, description="HTTP 상태 코드")
    weather: WeatherDetail = Field(..., description="날씨 정보")
    timeStamp: str = Field(..., description="응답 시간 (ISO 형식)")
    path: str = Field(..., description="요청 경로")

