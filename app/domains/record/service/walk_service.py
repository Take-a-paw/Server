from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import pytz

from app.core.firebase import verify_firebase_token
from app.core.error_handler import error_response
from app.models.user import User
from app.models.pet import Pet
from app.models.family_member import FamilyMember
from app.domains.record.repository.walk_repository import RecordWalkRepository


class RecordWalkService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = RecordWalkRepository(db)

    def list_walks(
        self,
        request: Request,
        authorization: Optional[str],
        pet_id: Optional[int],
        start_date: Optional[str],
        end_date: Optional[str],
    ):
        path = request.url.path

        # 1) Authorization 검증
        if authorization is None:
            return error_response(401, "WALK_LIST_401_1", "Authorization 헤더가 필요합니다.", path)

        if not authorization.startswith("Bearer "):
            return error_response(401, "WALK_LIST_401_2", "Authorization 헤더는 'Bearer <token>' 형식이어야 합니다.", path)

        parts = authorization.split(" ")
        if len(parts) != 2:
            return error_response(401, "WALK_LIST_401_2", "Authorization 헤더 형식이 잘못되었습니다.", path)

        id_token = parts[1]
        decoded = verify_firebase_token(id_token)
        if decoded is None:
            return error_response(401, "WALK_LIST_401_2", "유효하지 않거나 만료된 Firebase ID Token입니다. 다시 로그인해주세요.", path)

        firebase_uid = decoded.get("uid")

        # 2) pet_id 필수
        if pet_id is None:
            return error_response(400, "WALK_LIST_400_1", "pet_id 쿼리 파라미터는 필수입니다.", path)

        # 3) 사용자 조회
        user: User = (
            self.db.query(User)
            .filter(User.firebase_uid == firebase_uid)
            .first()
        )
        if not user:
            return error_response(404, "WALK_LIST_404_1", "해당 사용자를 찾을 수 없습니다.", path)

        # 4) 반려동물 조회
        pet: Pet = (
            self.db.query(Pet)
            .filter(Pet.pet_id == pet_id)
            .first()
        )
        if not pet:
            return error_response(404, "WALK_LIST_404_2", "요청하신 반려동물을 찾을 수 없습니다.", path)

        # 5) 권한 체크
        family_member: FamilyMember = (
            self.db.query(FamilyMember)
            .filter(
                FamilyMember.family_id == pet.family_id,
                FamilyMember.user_id == user.user_id
            )
            .first()
        )
        if not family_member:
            return error_response(403, "WALK_LIST_403_1", "해당 반려동물의 산책 기록을 조회할 권한이 없습니다.", path)

        # 6) 날짜 파싱 (KST -> UTC 경계 계산)
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
                return error_response(400, "WALK_LIST_400_3", "start_date는 end_date보다 이후일 수 없습니다.", path)
        except ValueError:
            return error_response(400, "WALK_LIST_400_2", "start_date와 end_date는 'YYYY-MM-DD' 형식이어야 합니다.", path)

        # 7) 조회
        try:
            walks = self.repo.list_walks(pet_id=pet_id, start_dt=start_dt_utc, end_dt=end_dt_utc)
        except Exception as e:
            print("WALK_LIST_QUERY_ERROR:", e)
            return error_response(500, "WALK_LIST_500_1", "산책 목록을 조회하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.", path)

        # 8) 응답
        items = []
        for w in walks:
            items.append({
                "walk_id": w.walk_id,
                "pet_id": w.pet_id,
                "user_id": w.user_id,
                "start_time": w.start_time.isoformat() if w.start_time else None,
                "end_time": w.end_time.isoformat() if w.end_time else None,
                "duration_min": w.duration_min,
                "distance_km": float(w.distance_km) if w.distance_km is not None else None,
                "calories": float(w.calories) if w.calories is not None else None,
                "weather_status": w.weather_status,
                "weather_temp_c": float(w.weather_temp_c) if w.weather_temp_c is not None else None,
            })

        response_content = {
            "success": True,
            "status": 200,
            "walks": items,
            "timeStamp": datetime.utcnow().isoformat(),
            "path": path
        }
        return JSONResponse(status_code=200, content=jsonable_encoder(response_content))
