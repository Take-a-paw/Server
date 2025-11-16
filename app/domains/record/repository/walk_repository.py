from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime
from typing import List, Optional

from app.models.walk import Walk
from app.models.walk_tracking_point import WalkTrackingPoint
from app.models.photo import Photo
from app.models.pet import Pet
from app.models.family import Family
from app.models.user import User


class RecordWalkRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_walks(
        self,
        pet_id: int,
        start_dt: Optional[datetime] = None,
        end_dt: Optional[datetime] = None,
    ) -> List[Walk]:
        query = self.db.query(Walk).filter(Walk.pet_id == pet_id)

        if start_dt is not None:
            query = query.filter(Walk.start_time >= start_dt)
        if end_dt is not None:
            query = query.filter(Walk.start_time <= end_dt)

        return (
            query
            .order_by(Walk.start_time.desc())
            .all()
        )

    def get_walk(self, walk_id: int) -> Optional[Walk]:
        return (
            self.db.query(Walk)
            .filter(Walk.walk_id == walk_id)
            .first()
        )

    def get_pet_and_family(self, pet_id: int) -> tuple[Optional[Pet], Optional[Family]]:
        pet = self.db.query(Pet).filter(Pet.pet_id == pet_id).first()
        family = None
        if pet:
            family = self.db.query(Family).filter(Family.family_id == pet.family_id).first()
        return pet, family

    def get_user(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.user_id == user_id).first()

    def get_points(self, walk_id: int) -> List[WalkTrackingPoint]:
        return (
            self.db.query(WalkTrackingPoint)
            .filter(WalkTrackingPoint.walk_id == walk_id)
            .order_by(WalkTrackingPoint.timestamp.asc())
            .all()
        )

    def get_photos(self, walk_id: int) -> List[Photo]:
        return (
            self.db.query(Photo)
            .filter(Photo.walk_id == walk_id)
            .order_by(Photo.created_at.asc())
            .all()
        )

    def list_recent_activities(self, pet_id: int, limit: int = 3) -> List[tuple]:
        return (
            self.db.query(Walk, User)
            .join(User, Walk.user_id == User.user_id)
            .filter(Walk.pet_id == pet_id)
            .order_by(Walk.start_time.desc())
            .limit(limit)
            .all()
        )
