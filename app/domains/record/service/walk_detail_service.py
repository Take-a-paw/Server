from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.firebase import verify_firebase_token
from app.domains.record.exception import record_error
from app.models.user import User
from app.models.family_member import FamilyMember
from app.domains.record.repository.walk_repository import RecordWalkRepository


class RecordWalkDetailService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = RecordWalkRepository(db)

    def get_walk_detail(
        self,
        request: Request,
        authorization: Optional[str],
        walk_id: int,
        include_points: Optional[str] = None,
    ):
        path = request.url.path

        # 1) Authorization 검증
        if authorization is None:
            return record_error("WALK_DETAIL_401_1", path)

        if not authorization.startswith("Bearer "):
            return record_error("WALK_DETAIL_401_2", path)

        parts = authorization.split(" ")
        if len(parts) != 2:
            return record_error("WALK_DETAIL_401_2", path)

        id_token = parts[1]
        decoded = verify_firebase_token(id_token)
        if decoded is None:
            return record_error("WALK_DETAIL_401_2", path)

        firebase_uid = decoded.get("uid")

        # 2) include_points 파싱 (선택)
        include_pts = False
        if include_points is not None:
            if include_points.lower() in ["true", "1", "yes"]:
                include_pts = True
            elif include_points.lower() in ["false", "0", "no", ""]:
                include_pts = False
            else:
                return record_error("WALK_DETAIL_400_1", path)

        # 3) 사용자 조회
        user: User = (
            self.db.query(User)
            .filter(User.firebase_uid == firebase_uid)
            .first()
        )
        if not user:
            return record_error("WALK_DETAIL_404_1", path)

        # 4) 산책 조회
        try:
            walk = self.repo.get_walk(walk_id)
            if not walk:
                return record_error("WALK_DETAIL_404_2", path)
        except Exception as e:
            print("WALK_DETAIL_QUERY_ERROR:", e)
            return record_error("WALK_DETAIL_500_1", path)

        # 5) 권한 체크 (family_members)
        pet, family = self.repo.get_pet_and_family(walk.pet_id)
        if not pet:
            return record_error("WALK_DETAIL_404_2", path)

        family_member: FamilyMember = (
            self.db.query(FamilyMember)
            .filter(
                FamilyMember.family_id == pet.family_id,
                FamilyMember.user_id == user.user_id
            )
            .first()
        )
        if not family_member:
            return record_error("WALK_DETAIL_403_1", path)

        # 6) 연관 데이터 조회
        walker = self.repo.get_user(walk.user_id)
        photos = self.repo.get_photos(walk.walk_id)
        points = self.repo.get_points(walk.walk_id) if include_pts else []

        # route_data는 현재 Walk 모델에 별도 저장소가 없으므로 None 처리 또는 확장 여지
        route_data = None
        thumbnail_url = photos[0].image_url if photos else None

        # 7) 응답 구성
        response_content = {
            "success": True,
            "status": 200,
            "walk": {
                "walk_id": walk.walk_id,
                "pet": {
                    "pet_id": pet.pet_id,
                    "name": pet.name,
                    "image_url": pet.image_url,
                    "family_id": pet.family_id,
                    "family_name": family.family_name if family else None,
                },
                "walker": {
                    "user_id": walker.user_id if walker else None,
                    "nickname": walker.nickname if walker else None,
                    "profile_img_url": walker.profile_img_url if walker else None,
                },
                "start_time": walk.start_time.isoformat() if walk.start_time else None,
                "end_time": walk.end_time.isoformat() if walk.end_time else None,
                "duration_min": walk.duration_min,
                "distance_km": float(walk.distance_km) if walk.distance_km is not None else None,
                "calories": float(walk.calories) if walk.calories is not None else None,
                "weather_status": walk.weather_status,
                "weather_temp_c": float(walk.weather_temp_c) if walk.weather_temp_c is not None else None,
                "thumbnail_image_url": thumbnail_url,
                "route_data": route_data,
                "points": [
                    {
                        "point_id": p.point_id,
                        "latitude": float(p.latitude),
                        "longitude": float(p.longitude),
                        "timestamp": p.timestamp.isoformat() if p.timestamp else None,
                    } for p in points
                ] if include_pts else None,
                "photos": [
                    {
                        "photo_id": ph.photo_id,
                        "image_url": ph.image_url,
                        "uploaded_by": ph.uploaded_by,
                        "caption": ph.caption,
                        "created_at": ph.created_at.isoformat() if ph.created_at else None,
                    } for ph in photos
                ],
            },
            "timeStamp": datetime.utcnow().isoformat(),
            "path": path
        }

        return JSONResponse(status_code=200, content=jsonable_encoder(response_content))
