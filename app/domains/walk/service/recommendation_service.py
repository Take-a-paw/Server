from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.firebase import verify_firebase_token
from app.core.error_handler import error_response
from app.models.user import User
from app.models.pet import Pet
from app.models.family_member import FamilyMember
from app.domains.walk.repository.recommendation_repository import RecommendationRepository


class RecommendationService:
    def __init__(self, db: Session):
        self.db = db
        self.recommendation_repo = RecommendationRepository(db)

    def get_recommendation(
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
                401, "WALK_REC_401_1", "Authorization 헤더가 필요합니다.", path
            )

        if not authorization.startswith("Bearer "):
            return error_response(
                401, "WALK_REC_401_2",
                "Authorization 헤더는 'Bearer <token>' 형식이어야 합니다.",
                path
            )

        parts = authorization.split(" ")
        if len(parts) != 2:
            return error_response(
                401, "WALK_REC_401_2",
                "Authorization 헤더 형식이 잘못되었습니다.",
                path
            )

        id_token = parts[1]
        decoded = verify_firebase_token(id_token)

        if decoded is None:
            return error_response(
                401, "WALK_REC_401_2",
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
                404, "WALK_REC_404_1",
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
                404, "WALK_REC_404_2",
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
                403, "WALK_REC_403_1",
                "해당 반려동물의 추천 정보를 조회할 권한이 없습니다.",
                path
            )

        # ============================================
        # 5) 추천 산책 정보 조회
        # ============================================
        try:
            recommendation = self.recommendation_repo.get_recommendation_by_pet_id(pet_id)

            if not recommendation:
                return error_response(
                    404, "WALK_REC_404_3",
                    "해당 반려동물의 추천 산책 정보가 아직 생성되지 않았습니다.",
                    path
                )

        except Exception as e:
            print("RECOMMENDATION_QUERY_ERROR:", e)
            return error_response(
                500, "WALK_REC_500_1",
                "추천 산책 정보를 조회하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                path
            )

        # ============================================
        # 6) 응답 생성
        # ============================================
        # per_walk 계산 (추천 산책 횟수로 나눔)
        recommended_minutes_per_walk = (
            recommendation.recommended_minutes // recommendation.recommended_walks
            if recommendation.recommended_walks > 0 else 0
        )
        recommended_distance_km_per_walk = (
            float(recommendation.recommended_distance_km) / recommendation.recommended_walks
            if recommendation.recommended_walks > 0 else 0.0
        )

        response_content = {
            "success": True,
            "status": 200,
            "recommendation": {
                "pet_id": recommendation.pet_id,
                "min_walks": recommendation.min_walks,
                "min_minutes": recommendation.min_minutes,
                "min_distance_km": float(recommendation.min_distance_km),
                "recommended_walks": recommendation.recommended_walks,
                "recommended_minutes": recommendation.recommended_minutes,
                "recommended_distance_km": float(recommendation.recommended_distance_km),
                "max_walks": recommendation.max_walks,
                "max_minutes": recommendation.max_minutes,
                "max_distance_km": float(recommendation.max_distance_km),
                "generated_by": recommendation.generated_by,
                "updated_at": recommendation.updated_at.isoformat() if recommendation.updated_at else None,
                "per_walk": {
                    "recommended_minutes_per_walk": recommended_minutes_per_walk,
                    "recommended_distance_km_per_walk": round(recommended_distance_km_per_walk, 2)
                }
            },
            "timeStamp": datetime.utcnow().isoformat(),
            "path": path
        }

        encoded = jsonable_encoder(response_content)
        return JSONResponse(status_code=200, content=encoded)


