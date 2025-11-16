from pydantic import BaseModel, Field


class TodayWalkDetail(BaseModel):
    """오늘 산책 현황 상세"""
    pet_id: int = Field(..., description="반려동물 ID")
    date: str = Field(..., description="날짜 (YYYY-MM-DD 형식)")
    total_walks: int = Field(..., description="누적 산책 횟수")
    total_duration_min: int = Field(..., description="총 산책 시간 (분)")
    total_distance_km: float = Field(..., description="총 이동 거리 (km)")
    current_walk_order: int = Field(..., description="지금 몇 번째 산책인지")
    has_ongoing_walk: bool = Field(..., description="진행 중인 산책이 있는지")


class TodayWalkResponse(BaseModel):
    """오늘 산책 현황 조회 응답"""
    success: bool = Field(True, description="성공 여부")
    status: int = Field(200, description="HTTP 상태 코드")
    today: TodayWalkDetail = Field(..., description="오늘 산책 현황")
    timeStamp: str = Field(..., description="응답 시간 (ISO 형식)")
    path: str = Field(..., description="요청 경로")

