# app/domains/walk/repository/walk_repository.py

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.walk import Walk
from app.models.family_member import FamilyMember
from app.models.pet import Pet


class RankingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_family_members(self, family_id: int):
        return (
            self.db.query(FamilyMember.user_id)
            .filter(FamilyMember.family_id == family_id)
            .all()
        )

    def check_family_exists(self, family_id: int):
        return (
            self.db.query(FamilyMember)
            .filter(FamilyMember.family_id == family_id)
            .first()
        )

    def get_walk_stats(self, user_ids, start_dt, end_dt, pet_id=None):
        query = (
            self.db.query(
                Walk.user_id,
                func.sum(Walk.distance_km).label("total_distance_km"),
                func.sum(Walk.duration_minutes).label("total_duration_min"),
                func.count(Walk.walk_id).label("walk_count"),
            )
            .filter(Walk.user_id.in_(user_ids))
            .filter(Walk.start_time >= start_dt)
            .filter(Walk.start_time <= end_dt)
        )

        if pet_id:
            query = query.filter(Walk.pet_id == pet_id)

        query = query.group_by(Walk.user_id)
        return query.all()

    def get_user_pets(self, user_id, start_dt, end_dt):
        """유저가 이번 기간 동안 산책한 pet 목록"""
        return (
            self.db.query(
                Pet.pet_id,
                Pet.name,
                Pet.image_url,
            )
            .join(Walk, Walk.pet_id == Pet.pet_id)
            .filter(Walk.user_id == user_id)
            .filter(Walk.start_time >= start_dt)
            .filter(Walk.start_time <= end_dt)
            .group_by(Pet.pet_id)
            .all()
        )
