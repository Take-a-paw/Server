from pydantic import BaseModel, Field
from typing import Optional


class WalkGoalRequest(BaseModel):
    """목표 산책량 설정 요청"""
    target_walks: int = Field(..., description="목표 산책 횟수", gt=0)
    target_minutes: int = Field(..., description="목표 산책 시간 (분)", gt=0)
    target_distance_km: float = Field(..., description="목표 산책 거리 (km)", gt=0)


class WalkGoalPatchRequest(BaseModel):
    """목표 산책량 부분 수정 요청"""
    target_walks: Optional[int] = Field(None, description="목표 산책 횟수", gt=0)
    target_minutes: Optional[int] = Field(None, description="목표 산책 시간 (분)", gt=0)
    target_distance_km: Optional[float] = Field(None, description="목표 산책 거리 (km)", gt=0)


class WalkGoalDetail(BaseModel):
    """목표 산책량 상세"""
    pet_id: int = Field(..., description="반려동물 ID")
    target_walks: int = Field(..., description="목표 산책 횟수")
    target_minutes: int = Field(..., description="목표 산책 시간 (분)")
    target_distance_km: float = Field(..., description="목표 산책 거리 (km)")
    created_at: Optional[str] = Field(None, description="생성 시간 (ISO 형식)")
    updated_at: Optional[str] = Field(None, description="업데이트 시간 (ISO 형식)")


class WalkGoalResponse(BaseModel):
    """목표 산책량 설정 응답"""
    success: bool = Field(True, description="성공 여부")
    status: int = Field(200, description="HTTP 상태 코드")
    goal: WalkGoalDetail = Field(..., description="목표 산책량 정보")
    timeStamp: str = Field(..., description="응답 시간 (ISO 형식)")
    path: str = Field(..., description="요청 경로")

