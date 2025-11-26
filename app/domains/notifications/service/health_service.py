# app/domains/notifications/service/health_service.py

import json
from datetime import datetime
from fastapi.responses import JSONResponse
from openai import OpenAI

from app.core.config import settings
from app.core.firebase import verify_firebase_token
from app.core.error_handler import error_response

from app.models.user import User
from app.models.notification import NotificationType

from app.domains.notifications.repository.notification_repository import NotificationRepository
from app.domains.notifications.repository.health_repository import HealthRepository


class HealthService:
    def __init__(self, db):
        self.db = db
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.health_repo = HealthRepository(db)
        self.notif_repo = NotificationRepository(db)

    # ============================================================
    # 🔥 GPT 건강 피드백 생성 함수 (수동/자동 공용)
    # ============================================================
    def _generate_health_advice(self, pet, weekly_minutes, rec_info):
        prompt = f"""
        너는 전문 수의사 겸 반려동물 건강 코치야.

        아래 정보를 종합 분석하고 사용자에게 줄
        **건강 관리 요약 피드백**을 JSON으로 생성해줘.

        반드시 출력 JSON 구조:
        {{
            "title": "string",
            "message": "string",
            "tags": ["string", "string"]
        }}

        --- 반려동물 정보 ---
        이름: {pet.name}
        견종: {pet.breed}
        나이: {pet.age}
        체중: {pet.weight}
        질병: {pet.disease}

        --- 최근 산책량 ---
        지난 7일 산책 시간: {weekly_minutes}분

        --- 추천 산책 정보 ---
        최소: {rec_info["min_minutes"]}
        적정: {rec_info["recommended_minutes"]}
        최대: {rec_info["max_minutes"]}

        message는 2~4문장으로 간결하게.
        title은 한 문장 요약.
        tags는 2~3개 핵심 키워드만.

        반드시 JSON만 출력.
        """

        try:
            gpt_res = self.client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.4,
                messages=[
                    {"role": "system", "content": "Output only JSON."},
                    {"role": "user", "content": prompt},
                ],
            )

            raw = gpt_res.choices[0].message.content.strip()
            cleaned = raw.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)

        except Exception as e:
            print("GPT ERROR:", e)
            return None

    # ============================================================
    # 🔥 건강 피드백 API (사용자 요청 → 가족 Broadcast)
    # ============================================================
    def generate_health_feedback(self, request, authorization, body):
        path = request.url.path

        # ------------------ AUTH ------------------
        if not authorization or not authorization.startswith("Bearer "):
            return error_response(401, "HEALTH_401_1", "Authorization 필요", path)

        decoded = verify_firebase_token(authorization.split(" ")[1])
        if decoded is None:
            return error_response(401, "HEALTH_401_2", "잘못된 토큰입니다.", path)

        firebase_uid = decoded["uid"]
        user = self.db.query(User).filter(User.firebase_uid == firebase_uid).first()
        if not user:
            return error_response(404, "HEALTH_404_1", "사용자를 찾을 수 없습니다.", path)

        # ------------------ PET ------------------
        pet = self.health_repo.get_pet(body.pet_id)
        if not pet:
            return error_response(404, "HEALTH_404_2", "반려동물을 찾을 수 없습니다.", path)

        # ------------------ 권한 체크 ------------------
        if not self.health_repo.user_in_family(user.user_id, pet.family_id):
            return error_response(403, "HEALTH_403_1", "해당 반려동물의 Family가 아닙니다.", path)

        # ------------------ 최근 산책량 ------------------
        weekly_minutes = self.health_repo.get_weekly_walk_minutes(pet.pet_id)

        # ------------------ 추천 산책 정보 ------------------
        rec = self.health_repo.get_recommendation(pet.pet_id)
        rec_info = {
            "min_minutes": rec.min_minutes if rec else None,
            "recommended_minutes": rec.recommended_minutes if rec else None,
            "max_minutes": rec.max_minutes if rec else None,
        }

        # ------------------ GPT ------------------
        advice = self._generate_health_advice(pet, weekly_minutes, rec_info)
        if advice is None:
            return error_response(500, "HEALTH_500_1", "LLM 분석 중 오류 발생", path)

        # ============================================================
        # 🔥 Notification 생성 (가족 전체 Broadcast)
        # ============================================================
        try:
            notif = self.notif_repo.create_notification(
                family_id=pet.family_id,
                target_user_id=None,   # ⭐ Broadcast (중요)
                related_pet_id=pet.pet_id,
                related_user_id=user.user_id,  # 누가 요청했는지 기록
                notif_type=NotificationType.SYSTEM_HEALTH,
                title=advice["title"],
                message=advice["message"],
            )
            self.db.commit()

        except Exception as e:
            print("NOTIF SAVE ERROR:", e)
            self.db.rollback()
            return error_response(500, "HEALTH_500_2", "알림 저장 중 오류 발생", path)

        # ============================================================
        # 응답
        # ============================================================
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "status": 200,
                "notification": {
                    "notification_id": notif.notification_id,
                    "type": "SYSTEM_HEALTH",
                    "title": notif.title,
                    "message": notif.message,
                    "family_id": pet.family_id,
                    "related_pet_id": pet.pet_id,
                    "related_user_id": user.user_id,
                    "created_at": notif.created_at.isoformat(),
                },
                "advice": advice,
                "weekly_walk_minutes": weekly_minutes,
                "recommended_info": rec_info,
                "timeStamp": datetime.utcnow().isoformat(),
                "path": path,
            },
        )


    # ============================================================
    # 🔁 정기 건강 추천 (매일 자동) → Broadcast
    # ============================================================
    def generate_auto_health_for_pet(self, pet_id: int):
        pet = self.health_repo.get_pet(pet_id)
        if not pet:
            print(f"[AUTO HEALTH] pet {pet_id} 없음")
            return

        weekly_minutes = self.health_repo.get_weekly_walk_minutes(pet.pet_id)
        rec = self.health_repo.get_recommendation(pet.pet_id)

        rec_info = {
            "min_minutes": rec.min_minutes if rec else None,
            "recommended_minutes": rec.recommended_minutes if rec else None,
            "max_minutes": rec.max_minutes if rec else None,
        }

        advice = self._generate_health_advice(pet, weekly_minutes, rec_info)
        if advice is None:
            print(f"[AUTO HEALTH] GPT 실패 (pet {pet_id})")
            return

        # ⭐ Broadcast
        notif = self.notif_repo.create_notification(
            family_id=pet.family_id,
            target_user_id=None,
            related_pet_id=pet.pet_id,
            related_user_id=None,
            notif_type=NotificationType.SYSTEM_HEALTH,
            title=advice["title"],
            message=advice["message"],
        )
        self.db.commit()

        print(f"[AUTO HEALTH] 발행 완료 - Pet {pet.pet_id} / 가족 {pet.family_id}")
