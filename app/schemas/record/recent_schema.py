from pydantic import BaseModel, Field
from typing import List, Optional


class WalkerBrief(BaseModel):
    user_id: int
    nickname: Optional[str]


class RecentActivityItem(BaseModel):
    walk_id: int
    date: str
    start_time: Optional[str]
    end_time: Optional[str]
    duration_min: Optional[int]
    distance_km: Optional[float]
    walker: WalkerBrief
    weather_status: Optional[str]
    weather_temp_c: Optional[float]


class RecentActivitiesResponse(BaseModel):
    success: bool = Field(True)
    status: int = Field(200)
    pet_id: int
    recent_activities: List[RecentActivityItem] = Field(default_factory=list)
    timeStamp: str
    path: str
