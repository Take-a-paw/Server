from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import pytz

from app.core.firebase import verify_firebase_token
from app.domains.record.exception import record_error
from app.models.user import User
from app.models.pet import Pet
from app.models.family_member import FamilyMember
from app.domains.record.repository.photo_repository import RecordPhotoRepository


class RecordPhotoService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = RecordPhotoRepository(db)

    def list_photos(
        self,
        request: Request,
        authorization: Optional[str],
        pet_id: Optional[int],
        start_date: Optional[str],
        end_date: Optional[str],
        page: int,
        size: int,
    ):
        path = request.url.path

        # 1) Authorization 검증
        if authorization is None:
            return record_error("PHOTO_LIST_401_1", path)
        if not authorization.startswith("Bearer "):
            return record_error("PHOTO_LIST_401_2", path)
        parts = authorization.split(" ")
        if len(parts) != 2:
            return record_error("PHOTO_LIST_401_2", path)
        decoded = verify_firebase_token(parts[1])
        if decoded is None:
            return record_error("PHOTO_LIST_401_2", path)

        firebase_uid = decoded.get("uid")

        # 2) pet_id 필수
        if pet_id is None:
            return record_error("PHOTO_LIST_400_3", path)

        # 3) 사용자/반려동물/권한 체크
        user: User = (
            self.db.query(User)
            .filter(User.firebase_uid == firebase_uid)
            .first()
        )
        if not user:
            return record_error("PHOTO_LIST_404_1", path)

        pet: Pet = (
            self.db.query(Pet)
            .filter(Pet.pet_id == pet_id)
            .first()
        )
        if not pet:
            return record_error("PHOTO_LIST_404_2", path)

        family_member: FamilyMember = (
            self.db.query(FamilyMember)
            .filter(
                FamilyMember.family_id == pet.family_id,
                FamilyMember.user_id == user.user_id
            )
            .first()
        )
        if not family_member:
            return record_error("PHOTO_LIST_403_1", path)

        # 4) 날짜 파싱 및 페이지 파라미터 처리
        start_dt_utc = None
        end_dt_utc = None
        try:
            kst = pytz.timezone('Asia/Seoul')
            if start_date:
                sd = datetime.strptime(start_date, "%Y-%m-%d")
                start_dt_utc = kst.localize(sd.replace(hour=0, minute=0, second=0, microsecond=0)).astimezone(pytz.UTC)
            if end_date:
                ed = datetime.strptime(end_date, "%Y-%m-%d")
                end_dt_utc = kst.localize(ed.replace(hour=23, minute=59, second=59, microsecond=999999)).astimezone(pytz.UTC)
            if start_dt_utc and end_dt_utc and start_dt_utc > end_dt_utc:
                return record_error("PHOTO_LIST_400_2", path)
        except ValueError:
            return record_error("PHOTO_LIST_400_1", path)

        page = page if page is not None and page >= 0 else 0
        size = size if size is not None and 1 <= size <= 100 else 20

        # 5) 조회
        try:
            rows, total = self.repo.list_photos(
                pet_id=pet_id,
                start_dt=start_dt_utc,
                end_dt=end_dt_utc,
                page=page,
                size=size,
            )
        except Exception as e:
            print("PHOTO_LIST_QUERY_ERROR:", e)
            return record_error("PHOTO_LIST_500_1", path)

        # 6) 응답 변환
        items = []
        for photo, walk, uploader in rows:
            items.append({
                "photo_id": photo.photo_id,
                "walk_id": walk.walk_id,
                "image_url": photo.image_url,
                "uploaded_by": {
                    "user_id": uploader.user_id,
                    "nickname": uploader.nickname,
                },
                "caption": photo.caption,
                "walk_date": walk.start_time.date().isoformat() if walk.start_time else None,
                "walk_start_time": walk.start_time.isoformat() if walk.start_time else None,
                "created_at": photo.created_at.isoformat() if photo.created_at else None,
            })

        response_content = {
            "success": True,
            "status": 200,
            "pet_id": pet_id,
            "photos": items,
            "page": page,
            "size": size,
            "total_count": total,
            "timeStamp": datetime.utcnow().isoformat(),
            "path": path
        }

        return JSONResponse(status_code=200, content=jsonable_encoder(response_content))
