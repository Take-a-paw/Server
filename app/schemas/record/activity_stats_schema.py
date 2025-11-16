from pydantic import BaseModel, Field
from typing import List, Optional


class Range(BaseModel):
    start_date: str
    end_date: str


class GoalSummary(BaseModel):
    has_goal: bool
    target_walks_per_day: Optional[int] = None
    target_minutes_per_day: Optional[int] = None
    target_distance_km_per_day: Optional[float] = None
    achievement_rate_walks: Optional[float] = None
    achievement_rate_minutes: Optional[float] = None
    achievement_rate_distance: Optional[float] = None


class RecommendationSummary(BaseModel):
    has_recommendation: bool
    recommended_walks_per_day: Optional[int] = None
    recommended_minutes_per_day: Optional[int] = None
    recommended_distance_km_per_day: Optional[float] = None


class Summary(BaseModel):
    pet_id: int
    total_walks: int
    total_distance_km: float
    total_duration_min: int
    active_days: int
    total_days: int
    avg_walks_per_day: float
    avg_distance_km_per_day: float
    avg_duration_min_per_day: float
    goal: GoalSummary
    recommendation: RecommendationSummary


class ChartPoint(BaseModel):
    date: str
    total_walks: int
    total_distance_km: float
    total_duration_min: int
    goal_walks: Optional[int] = None
    goal_minutes: Optional[int] = None
    goal_distance_km: Optional[float] = None


class Chart(BaseModel):
    granularity: str
    points: List[ChartPoint]


class ActivityStatsResponse(BaseModel):
    success: bool = Field(True)
    status: int = Field(200)
    period: str
    range: Range
    summary: Summary
    chart: Chart
    timeStamp: str
    path: str
