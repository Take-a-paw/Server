import json
import requests
from datetime import datetime
from fastapi import Request
from sqlalchemy.orm import Session
from typing import Optional

from openai import OpenAI

from app.core.config import settings
from app.core.firebase import verify_firebase_token
from app.core.error_handler import error_response

from app.models.user import User
from app.models.pet import Pet
from app.models.family_member import FamilyMember
from app.models.notification import NotificationType

from app.domains.notifications.repository.notification_repository import NotificationRepository
from app.domains.walk.repository.recommendation_repository import RecommendationRepository

from app.schemas.notifications.common_action_schema import (
    NotificationActionResponse,
    NotificationActionItem,
)
from app.schemas.walk.walk_recommendation_request_schema import WalkRecommendationRequest


class WalkRecommendationService:
    def __init__(self, db: Session):
        self.db = db
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.notif_repo = NotificationRepository(db)
        self.recommendation_repo = RecommendationRepository(db)

    def fetch_weather(self, lat: float, lng: float):
        """외부 날씨 API 호출"""
        try:
            url = (
                f"https://api.openweathermap.org/data/2.5/weather?"
                f"lat={lat}&lon={lng}&appid={settings.OPENWEATHER_API_KEY}"
                f"&units=metric&lang=kr"
            )
            res = requests.get(url, timeout=5)
            if res.status_code != 200:
                print("WEATHER API ERROR:", res.text)
                return None

            d = res.json()
            return {
                "status": d["weather"][0]["main"],
                "status_ko": d["weather"][0]["description"],
                "temp_c": d["main"]["temp"],
            }
        except Exception as e:
            print("WEATHER FETCH ERROR:", e)
            return None

    def generate_walk_recommendation(
        self, pet: Pet, weather_status: Optional[str], weather_temp_c: Optional[float],
        today_walk_count: Optional[int], today_total_distance_km: Optional[float]
    ):
        """OpenAI를 사용하여 산책 추천 멘트 생성"""
        prompt = f"""
        너는 반려동물 산책 전문가야.
        다음 정보를 바탕으로 간단한 산책 추천 멘트를 작성해줘.

        펫 정보:
        - 이름: {pet.name}
        - 종: {pet.breed}
        - 나이: {pet.age}세
        - 체중: {pet.weight}kg
        - 질병: {pet.disease if pet.disease else "없음"}

        위 정보를 바탕으로 다음 형식으로만 간단하게 작성해주세요:
        "{pet.name}는 하루에 {{횟수}}번 {{시간}}시간씩 {{거리}}km를 산책하는게 좋아요!"

        주의사항:
        - 인사말이나 긴 설명 없이 위 형식 그대로만 작성
        - 횟수, 시간, 거리는 펫의 종, 나이, 체중을 고려하여 적절한 값으로 설정
        - 한 문장으로만 작성 (30자 이내)
        - 예시: "댕댕이는 하루에 5번 1시간씩 3km를 산책하는게 좋아요!"

        JSON 형식:
        {{
            "title": "산책 추천",
            "message": "멘트 내용"
        }}
        """

        try:
            res = self.client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.7,
                messages=[
                    {"role": "system", "content": "Output JSON only."},
                    {"role": "user", "content": prompt},
                ],
            )

            raw = res.choices[0].message.content.strip()
            cleaned = raw.replace("```json", "").replace("```", "").strip()
            advice = json.loads(cleaned)

            # fallback
            if not isinstance(advice.get("title"), str):
                advice["title"] = "산책 추천"
            if not isinstance(advice.get("message"), str):
                advice["message"] = f"{pet.name}는 하루에 3번 30분씩 2km를 산책하는게 좋아요!"

            return advice
        except Exception as e:
            print("WALK RECOMMENDATION GPT ERROR:", e)
            return None

    def generate_recommendation(
        self,
        request: Request,
        authorization: Optional[str],
        body: WalkRecommendationRequest,
    ):
        path = request.url.path

        # 1) 인증
        if not authorization or not authorization.startswith("Bearer "):
            return error_response(401, "WALK_REC_401_1", "Authorization 헤더가 필요합니다.", path)

        decoded = verify_firebase_token(authorization.split(" ")[1])
        if decoded is None:
            return error_response(401, "WALK_REC_401_2", "유효하지 않거나 만료된 Firebase ID Token입니다.", path)

        firebase_uid = decoded.get("uid")

        # 2) 사용자 조회
        user: User = (
            self.db.query(User)
            .filter(User.firebase_uid == firebase_uid)
            .first()
        )
        if not user:
            return error_response(404, "WALK_REC_404_1", "해당 사용자를 찾을 수 없습니다.", path)

        # 3) 반려동물 조회
        pet: Pet = (
            self.db.query(Pet)
            .filter(Pet.pet_id == body.pet_id)
            .first()
        )
        if not pet:
            return error_response(404, "WALK_REC_404_2", "요청하신 반려동물을 찾을 수 없습니다.", path)

        # 4) 권한 체크
        family_member: FamilyMember = (
            self.db.query(FamilyMember)
            .filter(
                FamilyMember.family_id == pet.family_id,
                FamilyMember.user_id == user.user_id
            )
            .first()
        )
        if not family_member:
            return error_response(403, "WALK_REC_403_1", "해당 반려동물의 산책 추천을 받을 권한이 없습니다.", path)

        # 5) 날씨 정보 처리
        weather_status = body.weather_status
        weather_temp_c = body.weather_temp_c

        # 요청에 날씨 정보가 없으면 API 호출
        if not weather_status or weather_temp_c is None:
            weather_data = self.fetch_weather(body.lat, body.lng)
            if weather_data:
                if not weather_status:
                    weather_status = weather_data.get("status_ko", weather_data.get("status"))
                if weather_temp_c is None:
                    weather_temp_c = weather_data.get("temp_c")

        # 6) OpenAI 호출하여 추천 멘트 생성
        advice = self.generate_walk_recommendation(
            pet=pet,
            weather_status=weather_status,
            weather_temp_c=weather_temp_c,
            today_walk_count=body.today_walk_count,
            today_total_distance_km=body.today_total_distance_km,
        )

        if advice is None:
            return error_response(500, "WALK_REC_500_1", "산책 추천 멘트를 생성하는 중 오류가 발생했습니다.", path)

        # 7) 알림 생성 (개인 알림, 읽음 처리 제외)
        notif = self.notif_repo.create_notification(
            family_id=pet.family_id,
            target_user_id=user.user_id,  # 개인 알림
            related_pet_id=pet.pet_id,
            related_user_id=user.user_id,
            # 산책 추천을 날씨 추천과 구분하기 위해 SYSTEM_REMINDER 타입 사용
            notif_type=NotificationType.SYSTEM_REMINDER,
            title=advice["title"],
            message=advice["message"],
        )
        self.db.commit()

        # 8) 응답 생성
        return NotificationActionResponse(
            success=True,
            status=200,
            notification=NotificationActionItem(
                notification_id=notif.notification_id,
                type=notif.type.value,
                title=notif.title,
                message=notif.message,
                family_id=pet.family_id,
                target_user_id=user.user_id,
                related_pet_id=pet.pet_id,
                related_user_id=user.user_id,
                created_at=notif.created_at,
            ),
            timeStamp=datetime.utcnow().isoformat(),
            path=path,
        )

