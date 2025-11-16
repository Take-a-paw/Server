from pydantic import BaseModel, Field
from typing import List, Optional


class WalkItem(BaseModel):
    walk_id: int = Field(..., description="산책 ID")
    pet_id: int = Field(..., description="반려동물 ID")
    user_id: int = Field(..., description="사용자 ID")
    start_time: str = Field(..., description="시작 시간 (ISO)")
    end_time: Optional[str] = Field(None, description="종료 시간 (ISO)")
    duration_min: Optional[int] = Field(None, description="산책 시간 (분)")
    distance_km: Optional[float] = Field(None, description="산책 거리 (km)")
    calories: Optional[float] = Field(None, description="소모 칼로리")
    weather_status: Optional[str] = Field(None, description="날씨 상태")
    weather_temp_c: Optional[float] = Field(None, description="기온 (℃)")


class WalkListResponse(BaseModel):
    success: bool = Field(True)
    status: int = Field(200)
    walks: List[WalkItem] = Field(default_factory=list)
    timeStamp: str = Field(...)
    path: str = Field(...)
