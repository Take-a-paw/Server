# app/schemas/walk/walk_ranking_schema.py

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.schemas.error_schema import ErrorResponse


class RankingPetSchema(BaseModel):
    pet_id: int = Field(..., description="반려동물 ID")
    name: str = Field(..., description="반려동물 이름")
    image_url: Optional[str] = Field(None, description="반려동물 이미지 URL")


class RankingItemSchema(BaseModel):
    rank: int = Field(..., description="순위 (1부터 시작)")
    user_id: int = Field(..., description="사용자 ID")
    nickname: str = Field(..., description="사용자 닉네임")
    profile_img_url: Optional[str] = Field(None, description="사용자 프로필 이미지 URL")

    total_distance_km: float = Field(..., description="총 산책 거리(km)")
    total_duration_min: int = Field(..., description="총 산책 시간(min)")
    walk_count: int = Field(..., description="총 산책 횟수")

    pets: List[RankingPetSchema] = Field(..., description="사용자가 산책한 반려동물 목록")
    is_myself: bool = Field(..., description="현재 사용자 본인인지 여부")

    class Config:
        from_attributes = True


class WalkRankingResponse(BaseModel):
    success: bool = True
    status: int = 200

    family_id: int
    period: str
    ranking: List[RankingItemSchema]
    total_count: int

    timeStamp: str
    path: str
