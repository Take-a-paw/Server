from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.firebase import verify_firebase_token
from app.domains.record.exception import record_error
from app.models.user import User
from app.models.pet import Pet
from app.models.family_member import FamilyMember
from app.domains.record.repository.walk_repository import RecordWalkRepository


class RecentActivityService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = RecordWalkRepository(db)

    def list_recent(
        self,
        request: Request,
        authorization: Optional[str],
        pet_id: Optional[int],
        limit: int = 3,
    ):
        path = request.url.path

        # 1) Authorization
        if authorization is None:
            return record_error("RECENT_ACT_401_1", path)
        if not authorization.startswith("Bearer "):
            return record_error("RECENT_ACT_401_2", path)
        parts = authorization.split(" ")
        if len(parts) != 2:
            return record_error("RECENT_ACT_401_2", path)
        decoded = verify_firebase_token(parts[1])
        if decoded is None:
            return record_error("RECENT_ACT_401_2", path)

        # 2) Required pet_id
        if pet_id is None:
            return record_error("RECENT_ACT_404_2", path)

        # 3) User & Pet & Permission
        firebase_uid = decoded.get("uid")
        user: User = (
            self.db.query(User)
            .filter(User.firebase_uid == firebase_uid)
            .first()
        )
        if not user:
            return record_error("RECENT_ACT_404_1", path)

        pet: Pet = (
            self.db.query(Pet)
            .filter(Pet.pet_id == pet_id)
            .first()
        )
        if not pet:
            return record_error("RECENT_ACT_404_2", path)

        fm: FamilyMember = (
            self.db.query(FamilyMember)
            .filter(FamilyMember.family_id == pet.family_id, FamilyMember.user_id == user.user_id)
            .first()
        )
        if not fm:
            return record_error("RECENT_ACT_403_1", path)

        # 4) Query recent
        try:
            rows = self.repo.list_recent_activities(pet_id=pet_id, limit=limit)
        except Exception as e:
            print("RECENT_QUERY_ERROR:", e)
            return record_error("RECENT_ACT_500_1", path)

        activities = []
        for walk, walker in rows:
            thumbnail_url = self.repo.get_thumbnail_url(walk.walk_id)
            activities.append({
                "walk_id": walk.walk_id,
                "date": walk.start_time.date().isoformat() if walk.start_time else None,
                "start_time": walk.start_time.isoformat() if walk.start_time else None,
                "end_time": walk.end_time.isoformat() if walk.end_time else None,
                "duration_min": walk.duration_min,
                "distance_km": float(walk.distance_km) if walk.distance_km is not None else None,
                "walker": {
                    "user_id": walker.user_id,
                    "nickname": walker.nickname,
                },
                "weather_status": walk.weather_status,
                "weather_temp_c": float(walk.weather_temp_c) if walk.weather_temp_c is not None else None,
                "thumbnail_image_url": thumbnail_url,
            })

        response_content = {
            "success": True,
            "status": 200,
            "pet_id": pet_id,
            "recent_activities": activities,
            "timeStamp": datetime.utcnow().isoformat(),
            "path": path
        }

        return JSONResponse(status_code=200, content=jsonable_encoder(response_content))
