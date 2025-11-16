from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PerWalkRecommendation(BaseModel):
    """한 번의 산책당 추천 정보"""
    recommended_minutes_per_walk: int = Field(..., description="추천 산책 시간 (분)")
    recommended_distance_km_per_walk: float = Field(..., description="추천 산책 거리 (km)")


class RecommendationDetail(BaseModel):
    """추천 산책 정보 상세"""
    pet_id: int = Field(..., description="반려동물 ID")
    min_walks: int = Field(..., description="최소 산책 횟수")
    min_minutes: int = Field(..., description="최소 산책 시간 (분)")
    min_distance_km: float = Field(..., description="최소 산책 거리 (km)")
    recommended_walks: int = Field(..., description="추천 산책 횟수")
    recommended_minutes: int = Field(..., description="추천 산책 시간 (분)")
    recommended_distance_km: float = Field(..., description="추천 산책 거리 (km)")
    max_walks: int = Field(..., description="최대 산책 횟수")
    max_minutes: int = Field(..., description="최대 산책 시간 (분)")
    max_distance_km: float = Field(..., description="최대 산책 거리 (km)")
    generated_by: str = Field(..., description="생성 주체 (예: LLM)")
    updated_at: Optional[str] = Field(None, description="업데이트 시간 (ISO 형식)")
    per_walk: PerWalkRecommendation = Field(..., description="한 번의 산책당 추천 정보")


class RecommendationResponse(BaseModel):
    """추천 산책 정보 조회 응답"""
    success: bool = Field(True, description="성공 여부")
    status: int = Field(200, description="HTTP 상태 코드")
    recommendation: RecommendationDetail = Field(..., description="추천 산책 정보")
    timeStamp: str = Field(..., description="응답 시간 (ISO 형식)")
    path: str = Field(..., description="요청 경로")


