from pydantic import BaseModel, Field
from typing import Optional, List


class PetBrief(BaseModel):
    pet_id: int
    name: Optional[str]
    image_url: Optional[str]
    family_id: Optional[int]
    family_name: Optional[str]


class WalkerBrief(BaseModel):
    user_id: int
    nickname: Optional[str]
    profile_img_url: Optional[str]


class RouteData(BaseModel):
    polyline: Optional[str]
    points_count: Optional[int]


class TrackPoint(BaseModel):
    point_id: int
    latitude: float
    longitude: float
    timestamp: str


class PhotoItem(BaseModel):
    photo_id: int
    image_url: str
    uploaded_by: int
    caption: Optional[str]
    created_at: Optional[str]


class WalkDetail(BaseModel):
    walk_id: int
    pet: PetBrief
    walker: WalkerBrief
    start_time: str
    end_time: Optional[str]
    duration_min: Optional[int]
    distance_km: Optional[float]
    calories: Optional[float]
    weather_status: Optional[str]
    weather_temp_c: Optional[float]
    route_data: Optional[RouteData]
    points: Optional[List[TrackPoint]]
    photos: List[PhotoItem] = []


class WalkDetailResponse(BaseModel):
    success: bool = Field(True)
    status: int = Field(200)
    walk: WalkDetail
    timeStamp: str
    path: str
