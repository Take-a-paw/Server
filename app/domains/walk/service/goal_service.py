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
from app.models.pet_walk_recommendation import PetWalkRecommendation
from app.domains.walk.repository.goal_repository import GoalRepository
from app.domains.walk.repository.recommendation_repository import RecommendationRepository
from app.schemas.walk.goal_schema import WalkGoalRequest, WalkGoalPatchRequest


class GoalService:
    def __init__(self, db: Session):
        self.db = db
        self.goal_repo = GoalRepository(db)
        self.recommendation_repo = RecommendationRepository(db)

    def set_goal(
        self,
        request: Request,
        authorization: Optional[str],
        pet_id: int,
        body: WalkGoalRequest,
    ):
        path = request.url.path

        # ============================================
        # 1) Authorization 검증
        # ============================================
        if authorization is None:
            return error_response(
                401, "WALK_GOAL_401_1", "Authorization 헤더가 필요합니다.", path
            )

        if not authorization.startswith("Bearer "):
            return error_response(
                401, "WALK_GOAL_401_2",
                "Authorization 헤더는 'Bearer <token>' 형식이어야 합니다.",
                path
            )

        parts = authorization.split(" ")
        if len(parts) != 2:
            return error_response(
                401, "WALK_GOAL_401_2",
                "Authorization 헤더 형식이 잘못되었습니다.",
                path
            )

        id_token = parts[1]
        decoded = verify_firebase_token(id_token)

        if decoded is None:
            return error_response(
                401, "WALK_GOAL_401_2",
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
                404, "WALK_GOAL_404_1",
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
                404, "WALK_GOAL_404_2",
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
                403, "WALK_GOAL_403_1",
                "해당 반려동물의 목표 산책량을 설정할 권한이 없습니다.",
                path
            )

        # ============================================
        # 5) Body 유효성 검사
        # ============================================
        # Pydantic이 이미 필수 필드, 형식, gt=0 검증을 처리하지만,
        # 요구사항에 맞는 명시적 에러 코드를 제공하기 위해 추가 검사
        
        # 5-1) 필수 필드 체크 (Pydantic이 처리하지만 명시적으로)
        if body.target_walks is None or body.target_minutes is None or body.target_distance_km is None:
            return error_response(
                400, "WALK_GOAL_400_1",
                "target_walks, target_minutes, target_distance_km는 모두 필수입니다.",
                path
            )

        # 5-2) 형식 및 0보다 큰 값 체크
        try:
            target_walks = int(body.target_walks)
            target_minutes = int(body.target_minutes)
            target_distance_km = float(body.target_distance_km)
            
            # 5-3) 0보다 큰지 체크
            if target_walks <= 0 or target_minutes <= 0 or target_distance_km <= 0:
                return error_response(
                    400, "WALK_GOAL_400_3",
                    "목표 산책 횟수, 시간, 거리는 0보다 커야 합니다.",
                    path
                )
        except (ValueError, TypeError):
            return error_response(
                400, "WALK_GOAL_400_2",
                "목표 산책 값의 형식이 올바르지 않습니다.",
                path
            )

        # 5-4) 건강에 무리가 가는 수준인지 체크 (pet_walk_recommendation과 비교)
        try:
            recommendation = self.recommendation_repo.get_recommendation_by_pet_id(pet_id)
            
            if recommendation:
                # recommended 값의 2배 이상이거나 max 값의 1.5배 이상이면 과도하다고 판단
                is_excessive = (
                    target_walks > recommendation.recommended_walks * 2 or
                    target_minutes > recommendation.recommended_minutes * 2 or
                    target_distance_km > float(recommendation.recommended_distance_km) * 2 or
                    target_walks > recommendation.max_walks * 1.5 or
                    target_minutes > recommendation.max_minutes * 1.5 or
                    target_distance_km > float(recommendation.max_distance_km) * 1.5
                )
                
                if is_excessive:
                    return error_response(
                        400, "WALK_GOAL_400_4",
                        "설정하신 목표 산책량이 반려동물의 건강에 무리가 갈 수 있습니다. 보다 현실적인 목표로 다시 설정해주세요.",
                        path
                    )
        except Exception as e:
            print("RECOMMENDATION_CHECK_ERROR:", e)
            # 추천 정보가 없어도 목표 설정은 가능하도록 함

        # ============================================
        # 6) 목표 산책량 설정 (생성 또는 업데이트)
        # ============================================
        try:
            existing_goal = self.goal_repo.get_goal_by_pet_id(pet_id)
            
            if existing_goal:
                # 업데이트
                goal = self.goal_repo.update_goal(
                    goal=existing_goal,
                    target_walks=target_walks,
                    target_minutes=target_minutes,
                    target_distance_km=target_distance_km,
                )
            else:
                # 생성
                goal = self.goal_repo.create_goal(
                    pet_id=pet_id,
                    target_walks=target_walks,
                    target_minutes=target_minutes,
                    target_distance_km=target_distance_km,
                )
            
            self.db.commit()
            self.db.refresh(goal)

        except Exception as e:
            print("GOAL_SAVE_ERROR:", e)
            self.db.rollback()
            return error_response(
                500, "WALK_GOAL_500_1",
                "목표 산책량을 저장하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                path
            )

        # ============================================
        # 7) 응답 생성
        # ============================================
        response_content = {
            "success": True,
            "status": 200,
            "goal": {
                "pet_id": goal.pet_id,
                "target_walks": goal.target_walks,
                "target_minutes": goal.target_minutes,
                "target_distance_km": float(goal.target_distance_km),
                "created_at": goal.created_at.isoformat() if goal.created_at else None,
                "updated_at": goal.updated_at.isoformat() if goal.updated_at else None,
            },
            "timeStamp": datetime.utcnow().isoformat(),
            "path": path
        }

        encoded = jsonable_encoder(response_content)
        return JSONResponse(status_code=200, content=encoded)

    def patch_goal(
        self,
        request: Request,
        authorization: Optional[str],
        goal_id: int,
        body: WalkGoalPatchRequest,
    ):
        path = request.url.path

        # ============================================
        # 1) Authorization 검증
        # ============================================
        if authorization is None:
            return error_response(
                401, "WALK_GOAL_PATCH_401_1", "Authorization 헤더가 필요합니다.", path
            )

        if not authorization.startswith("Bearer "):
            return error_response(
                401, "WALK_GOAL_PATCH_401_2",
                "Authorization 헤더는 'Bearer <token>' 형식이어야 합니다.",
                path
            )

        parts = authorization.split(" ")
        if len(parts) != 2:
            return error_response(
                401, "WALK_GOAL_PATCH_401_2",
                "Authorization 헤더 형식이 잘못되었습니다.",
                path
            )

        id_token = parts[1]
        decoded = verify_firebase_token(id_token)

        if decoded is None:
            return error_response(
                401, "WALK_GOAL_PATCH_401_2",
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
                404, "WALK_GOAL_PATCH_404_1",
                "해당 사용자를 찾을 수 없습니다.",
                path
            )

        # ============================================
        # 3) 목표 산책량 조회
        # ============================================
        goal = self.goal_repo.get_goal_by_goal_id(goal_id)

        if not goal:
            return error_response(
                404, "WALK_GOAL_PATCH_404_3",
                "해당 반려동물의 목표 산책량이 아직 설정되지 않았습니다.",
                path
            )

        # ============================================
        # 4) 반려동물 조회
        # ============================================
        pet: Pet = (
            self.db.query(Pet)
            .filter(Pet.pet_id == goal.pet_id)
            .first()
        )

        if not pet:
            return error_response(
                404, "WALK_GOAL_PATCH_404_2",
                "요청하신 반려동물을 찾을 수 없습니다.",
                path
            )

        # ============================================
        # 5) Owner 권한 체크 (owner만 수정 가능)
        # ============================================
        if pet.owner_id != user.user_id:
            return error_response(
                403, "WALK_GOAL_PATCH_403_1",
                "해당 반려동물의 목표 산책량을 수정할 권한이 없습니다.",
                path
            )

        # ============================================
        # 6) Body 유효성 검사
        # ============================================
        # 6-1) 수정할 필드가 하나도 없는지 체크
        if (body.target_walks is None and 
            body.target_minutes is None and 
            body.target_distance_km is None):
            return error_response(
                400, "WALK_GOAL_PATCH_400_1",
                "수정할 목표 산책 필드가 존재하지 않습니다.",
                path
            )

        # 6-2) 형식 및 0보다 큰 값 체크
        target_walks = body.target_walks
        target_minutes = body.target_minutes
        target_distance_km = body.target_distance_km

        # 수정할 값들만 검증
        try:
            if target_walks is not None:
                target_walks = int(target_walks)
                if target_walks <= 0:
                    return error_response(
                        400, "WALK_GOAL_PATCH_400_3",
                        "목표 산책 횟수, 시간, 거리는 0보다 커야 합니다.",
                        path
                    )
            
            if target_minutes is not None:
                target_minutes = int(target_minutes)
                if target_minutes <= 0:
                    return error_response(
                        400, "WALK_GOAL_PATCH_400_3",
                        "목표 산책 횟수, 시간, 거리는 0보다 커야 합니다.",
                        path
                    )
            
            if target_distance_km is not None:
                target_distance_km = float(target_distance_km)
                if target_distance_km <= 0:
                    return error_response(
                        400, "WALK_GOAL_PATCH_400_3",
                        "목표 산책 횟수, 시간, 거리는 0보다 커야 합니다.",
                        path
                    )
        except (ValueError, TypeError):
            return error_response(
                400, "WALK_GOAL_PATCH_400_2",
                "목표 산책 값의 형식이 올바르지 않습니다.",
                path
            )

        # 6-3) 건강에 무리가 가는 수준인지 체크 (pet_walk_recommendation과 비교)
        # 수정할 값과 기존 값을 합쳐서 최종 값 계산
        final_target_walks = target_walks if target_walks is not None else goal.target_walks
        final_target_minutes = target_minutes if target_minutes is not None else goal.target_minutes
        final_target_distance_km = target_distance_km if target_distance_km is not None else float(goal.target_distance_km)

        try:
            recommendation = self.recommendation_repo.get_recommendation_by_pet_id(pet.pet_id)
            
            if recommendation:
                # recommended 값의 2배 이상이거나 max 값의 1.5배 이상이면 과도하다고 판단
                is_excessive = (
                    final_target_walks > recommendation.recommended_walks * 2 or
                    final_target_minutes > recommendation.recommended_minutes * 2 or
                    final_target_distance_km > float(recommendation.recommended_distance_km) * 2 or
                    final_target_walks > recommendation.max_walks * 1.5 or
                    final_target_minutes > recommendation.max_minutes * 1.5 or
                    final_target_distance_km > float(recommendation.max_distance_km) * 1.5
                )
                
                if is_excessive:
                    return error_response(
                        400, "WALK_GOAL_PATCH_400_4",
                        "설정하신 목표 산책량이 반려동물의 건강에 무리가 갈 수 있습니다. 보다 현실적인 목표로 다시 설정해주세요.",
                        path
                    )
        except Exception as e:
            print("RECOMMENDATION_CHECK_ERROR:", e)
            # 추천 정보가 없어도 목표 수정은 가능하도록 함

        # ============================================
        # 7) 목표 산책량 부분 수정
        # ============================================
        try:
            updated_goal = self.goal_repo.partial_update_goal(
                goal=goal,
                target_walks=target_walks,
                target_minutes=target_minutes,
                target_distance_km=target_distance_km,
            )
            
            self.db.commit()
            self.db.refresh(updated_goal)

        except Exception as e:
            print("GOAL_UPDATE_ERROR:", e)
            self.db.rollback()
            return error_response(
                500, "WALK_GOAL_PATCH_500_1",
                "목표 산책량을 수정하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                path
            )

        # ============================================
        # 8) 응답 생성
        # ============================================
        response_content = {
            "success": True,
            "status": 200,
            "goal": {
                "pet_id": updated_goal.pet_id,
                "target_walks": updated_goal.target_walks,
                "target_minutes": updated_goal.target_minutes,
                "target_distance_km": float(updated_goal.target_distance_km),
                "created_at": updated_goal.created_at.isoformat() if updated_goal.created_at else None,
                "updated_at": updated_goal.updated_at.isoformat() if updated_goal.updated_at else None,
            },
            "timeStamp": datetime.utcnow().isoformat(),
            "path": path
        }

        encoded = jsonable_encoder(response_content)
        return JSONResponse(status_code=200, content=encoded)

