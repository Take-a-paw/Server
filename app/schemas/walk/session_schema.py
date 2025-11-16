from pydantic import BaseModel, Field
from typing import Optional


class WalkStartRequest(BaseModel):
    """산책 시작 요청"""
    pet_id: int = Field(..., description="반려동물 ID")
    start_lat: Optional[float] = Field(None, description="시작 위도")
    start_lng: Optional[float] = Field(None, description="시작 경도")


class WalkDetail(BaseModel):
    """산책 상세 정보"""
    walk_id: int = Field(..., description="산책 ID")
    pet_id: int = Field(..., description="반려동물 ID")
    user_id: int = Field(..., description="사용자 ID")
    start_time: str = Field(..., description="시작 시간 (ISO 형식)")
    end_time: Optional[str] = Field(None, description="종료 시간 (ISO 형식)")
    duration_min: Optional[int] = Field(None, description="산책 시간 (분)")
    distance_km: Optional[float] = Field(None, description="산책 거리 (km)")
    calories: Optional[float] = Field(None, description="소모 칼로리")
    weather_status: Optional[str] = Field(None, description="날씨 상태")
    weather_temp_c: Optional[float] = Field(None, description="기온 (℃)")
    created_at: Optional[str] = Field(None, description="생성 시간 (ISO 형식)")


class WalkStartResponse(BaseModel):
    """산책 시작 응답"""
    success: bool = Field(True, description="성공 여부")
    status: int = Field(201, description="HTTP 상태 코드")
    walk: WalkDetail = Field(..., description="산책 정보")
    timeStamp: str = Field(..., description="응답 시간 (ISO 형식)")
    path: str = Field(..., description="요청 경로")


class WalkTrackRequest(BaseModel):
    """산책 위치 기록 요청"""
    latitude: float = Field(..., description="위도")
    longitude: float = Field(..., description="경도")
    timestamp: str = Field(..., description="타임스탬프 (ISO 형식)")


class WalkTrackPointDetail(BaseModel):
    """산책 위치 포인트 상세"""
    point_id: int = Field(..., description="포인트 ID")
    walk_id: int = Field(..., description="산책 ID")
    latitude: float = Field(..., description="위도")
    longitude: float = Field(..., description="경도")
    timestamp: str = Field(..., description="타임스탬프 (ISO 형식)")


class WalkTrackResponse(BaseModel):
    """산책 위치 기록 응답"""
    success: bool = Field(True, description="성공 여부")
    status: int = Field(201, description="HTTP 상태 코드")
    point: WalkTrackPointDetail = Field(..., description="위치 포인트 정보")
    timeStamp: str = Field(..., description="응답 시간 (ISO 형식)")
    path: str = Field(..., description="요청 경로")


class RouteData(BaseModel):
    """경로 데이터"""
    polyline: Optional[str] = Field(None, description="인코딩된 폴리라인 문자열")
    points_count: Optional[int] = Field(None, description="포인트 개수")


class WalkEndRequest(BaseModel):
    """산책 종료 요청"""
    total_distance_km: Optional[float] = Field(None, description="총 이동 거리 (km)")
    total_duration_min: Optional[int] = Field(None, description="총 산책 시간 (분)")
    last_lat: Optional[float] = Field(None, description="마지막 위도")
    last_lng: Optional[float] = Field(None, description="마지막 경도")
    route_data: Optional[RouteData] = Field(None, description="경로 데이터")


class WalkEndDetail(BaseModel):
    """산책 종료 상세 정보"""
    walk_id: int = Field(..., description="산책 ID")
    pet_id: int = Field(..., description="반려동물 ID")
    user_id: int = Field(..., description="사용자 ID")
    start_time: str = Field(..., description="시작 시간 (ISO 형식)")
    end_time: str = Field(..., description="종료 시간 (ISO 형식)")
    duration_min: Optional[int] = Field(None, description="산책 시간 (분)")
    distance_km: Optional[float] = Field(None, description="산책 거리 (km)")
    calories: Optional[float] = Field(None, description="소모 칼로리")
    last_lat: Optional[float] = Field(None, description="마지막 위도")
    last_lng: Optional[float] = Field(None, description="마지막 경도")
    route_data: Optional[RouteData] = Field(None, description="경로 데이터")


class ActivityStatDetail(BaseModel):
    """활동 통계 상세"""
    date: str = Field(..., description="날짜 (YYYY-MM-DD)")
    pet_id: int = Field(..., description="반려동물 ID")
    total_walks: int = Field(..., description="총 산책 횟수")
    total_distance_km: float = Field(..., description="총 이동 거리 (km)")
    total_duration_min: int = Field(..., description="총 산책 시간 (분)")
    avg_speed_kmh: Optional[float] = Field(None, description="평균 속도 (km/h)")


class WalkEndResponse(BaseModel):
    """산책 종료 응답"""
    success: bool = Field(True, description="성공 여부")
    status: int = Field(200, description="HTTP 상태 코드")
    walk: WalkEndDetail = Field(..., description="산책 정보")
    activity_stats: ActivityStatDetail = Field(..., description="활동 통계")
    timeStamp: str = Field(..., description="응답 시간 (ISO 형식)")
    path: str = Field(..., description="요청 경로")

