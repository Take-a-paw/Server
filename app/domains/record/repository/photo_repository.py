from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional, Tuple
from datetime import datetime

from app.models.photo import Photo
from app.models.walk import Walk
from app.models.user import User


class RecordPhotoRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_photos(
        self,
        pet_id: int,
        start_dt: Optional[datetime],
        end_dt: Optional[datetime],
        page: int,
        size: int,
    ) -> Tuple[List[tuple], int]:
        """
        Returns a list of tuples (Photo, Walk, User) and total_count
        """
        query = (
            self.db.query(Photo, Walk, User)
            .join(Walk, Photo.walk_id == Walk.walk_id)
            .join(User, Photo.uploaded_by == User.user_id)
            .filter(Walk.pet_id == pet_id)
        )

        if start_dt is not None:
            query = query.filter(Walk.start_time >= start_dt)
        if end_dt is not None:
            query = query.filter(Walk.start_time <= end_dt)

        total_count = query.count()

        rows = (
            query
            .order_by(Photo.created_at.desc())
            .offset(page * size)
            .limit(size)
            .all()
        )

        return rows, total_count
