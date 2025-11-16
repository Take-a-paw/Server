from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import List, Dict

from app.models.walk import Walk
from app.models.pet_walk_goal import PetWalkGoal
from app.models.pet_walk_recommendation import PetWalkRecommendation


class StatsRepository:
    def __init__(self, db: Session):
        self.db = db

    def aggregate_daily(self, pet_id: int, start_utc: datetime, end_utc: datetime) -> List[Dict]:
        """
        Aggregate walks by UTC date (we will convert date boundaries beforehand using KST in service)
        Returns list of dicts with keys: date (date), total_walks, total_distance_km, total_duration_min
        """
        rows = (
            self.db.query(
                func.date(Walk.start_time).label("d"),
                func.count(Walk.walk_id).label("cnt"),
                func.coalesce(func.sum(Walk.distance_km), 0).label("dist"),
                func.coalesce(func.sum(Walk.duration_min), 0).label("dur"),
            )
            .filter(
                Walk.pet_id == pet_id,
                Walk.start_time >= start_utc,
                Walk.start_time <= end_utc,
            )
            .group_by(func.date(Walk.start_time))
            .order_by(func.date(Walk.start_time).asc())
            .all()
        )
        result = []
        for d, cnt, dist, dur in rows:
            result.append({
                "date": d.isoformat() if hasattr(d, 'isoformat') else str(d),
                "total_walks": int(cnt or 0),
                "total_distance_km": float(dist or 0.0),
                "total_duration_min": int(dur or 0),
            })
        return result

    def get_goal(self, pet_id: int) -> PetWalkGoal | None:
        return (
            self.db.query(PetWalkGoal)
            .filter(PetWalkGoal.pet_id == pet_id)
            .first()
        )

    def get_recommendation(self, pet_id: int) -> PetWalkRecommendation | None:
        return (
            self.db.query(PetWalkRecommendation)
            .filter(PetWalkRecommendation.pet_id == pet_id)
            .first()
        )
