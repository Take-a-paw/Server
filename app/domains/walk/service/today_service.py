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
from app.domains.walk.repository.today_repository import TodayRepository


class TodayService:
    def __init__(self, db: Session):
        self.db = db
        self.today_repo = TodayRepository(db)

    def get_today_walks(
        self,
        request: Request,
        authorization: Optional[str],
        pet_id: int,
    ):
        path = request.url.path

        # ============================================
        # 1) Authorization 검증
        # ============================================
        if authorization is None:
            return error_response(
                401, "WALK_TODAY_401_1", "Authorization 헤더가 필요합니다.", path
            )

        if not authorization.startswith("Bearer "):
            return error_response(
                401, "WALK_TODAY_401_2",
                "Authorization 헤더는 'Bearer <token>' 형식이어야 합니다.",
                path
            )

        parts = authorization.split(" ")
        if len(parts) != 2:
            return error_response(
                401, "WALK_TODAY_401_2",
                "Authorization 헤더 형식이 잘못되었습니다.",
                path
            )

        id_token = parts[1]
        decoded = verify_firebase_token(id_token)

        if decoded is None:
            return error_response(
                401, "WALK_TODAY_401_2",
                "유효하지 않거나 만료된 Firebase ID Token입니다. 다시 로그인해주세요.",
                path
            )

        firebase_uid = decoded.get("uid")

        # ============================================
        # 2) 사용자 조회
        # ============================================
        user: User = (
            self.db.query(User)
            .filter(User.firebase_uid == firebase_uid)
            .first()
        )

        if not user:
            return error_response(
                404, "WALK_TODAY_404_1",
                "해당 사용자를 찾을 수 없습니다.",
                path
            )

        # ============================================
        # 3) 반려동물 조회
        # ============================================
        pet: Pet = (
            self.db.query(Pet)
            .filter(Pet.pet_id == pet_id)
            .first()
        )

        if not pet:
            return error_response(
                404, "WALK_TODAY_404_2",
                "요청하신 반려동물을 찾을 수 없습니다.",
                path
            )

        # ============================================
        # 4) 권한 체크 (family_members 확인)
        # ============================================
        family_member: FamilyMember = (
            self.db.query(FamilyMember)
            .filter(
                FamilyMember.family_id == pet.family_id,
                FamilyMember.user_id == user.user_id
            )
            .first()
        )

        if not family_member:
            return error_response(
                403, "WALK_TODAY_403_1",
                "해당 반려동물의 산책 정보를 조회할 권한이 없습니다.",
                path
            )

        # ============================================
        # 5) 오늘 날짜 계산 (서버 타임존 기준, KST UTC+9)
        # ============================================
        try:
            # 한국 시간대 설정
            kst = pytz.timezone('Asia/Seoul')
            now_kst = datetime.now(kst)
            
            # 오늘 날짜의 시작과 끝 시간 계산 (KST 기준)
            today_start_kst = now_kst.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end_kst = now_kst.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # UTC로 변환 (DB에 저장된 시간이 UTC일 수 있으므로)
            today_start_utc = today_start_kst.astimezone(pytz.UTC)
            today_end_utc = today_end_kst.astimezone(pytz.UTC)
            
            # 날짜 문자열 (YYYY-MM-DD)
            today_date_str = now_kst.date().isoformat()

        except Exception as e:
            print("DATE_CALCULATION_ERROR:", e)
            return error_response(
                500, "WALK_TODAY_500_1",
                "오늘 산책 현황을 조회하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                path
            )

        # ============================================
        # 6) 오늘 산책 현황 조회
        # ============================================
        try:
            total_walks, total_duration_min, total_distance_km, current_walk_order, has_ongoing_walk = (
                self.today_repo.get_today_walks_stats(
                    pet_id=pet_id,
                    today_start=today_start_utc,
                    today_end=today_end_utc
                )
            )

        except Exception as e:
            print("WALK_STATS_QUERY_ERROR:", e)
            return error_response(
                500, "WALK_TODAY_500_1",
                "오늘 산책 현황을 조회하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                path
            )

        # ============================================
        # 7) 응답 생성
        # ============================================
        response_content = {
            "success": True,
            "status": 200,
            "today": {
                "pet_id": pet_id,
                "date": today_date_str,
                "total_walks": total_walks,
                "total_duration_min": total_duration_min,
                "total_distance_km": round(total_distance_km, 2),
                "current_walk_order": current_walk_order,
                "has_ongoing_walk": has_ongoing_walk
            },
            "timeStamp": datetime.utcnow().isoformat(),
            "path": path
        }

        encoded = jsonable_encoder(response_content)
        return JSONResponse(status_code=200, content=encoded)

