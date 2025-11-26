# app/domains/notifications/repository/weather_repository.py

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.pet import Pet
from app.models.family_member import FamilyMember
from app.models.pet_walk_recommendation import PetWalkRecommendation
from app.models.walk import Walk


class WeatherRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_pet(self, pet_id: int):
        return self.db.query(Pet).filter(Pet.pet_id == pet_id).first()

    def user_in_family(self, user_id: int, family_id: int) -> bool:
        return (
            self.db.query(FamilyMember)
            .filter(
                FamilyMember.user_id == user_id,
                FamilyMember.family_id == family_id,
            )
            .first()
            is not None
        )

    # 최근 7일 산책 시간 총합 (분)
    def get_weekly_walk_minutes(self, pet_id: int) -> int:
        now = datetime.utcnow()
        seven_days_ago = now - timedelta(days=7)

        total = (
            self.db.query(func.coalesce(func.sum(Walk.duration_min), 0))
            .filter(
                Walk.pet_id == pet_id,
                Walk.start_time >= seven_days_ago,
            )
            .scalar()
        )
        return int(total or 0)

    # 산책 추천 정보 조회
    def get_recommendation(self, pet_id: int):
        return (
            self.db.query(PetWalkRecommendation)
            .filter(PetWalkRecommendation.pet_id == pet_id)
            .first()
        )

    # 최근 산책 1건
    def get_last_walk_record(self, pet_id: int):
        return (
            self.db.query(Walk)
            .filter(Walk.pet_id == pet_id)
            .order_by(Walk.start_time.desc())
            .first()
        )
