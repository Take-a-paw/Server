# app/domains/notifications/service/weather_service.py

import json
import requests
from datetime import datetime
import pytz

from fastapi.responses import JSONResponse
from openai import OpenAI

from app.core.config import settings
from app.core.firebase import verify_firebase_token
from app.core.error_handler import error_response

from app.models.user import User
from app.models.notification import NotificationType
from app.models.notification_reads import NotificationRead
from app.domains.notifications.repository.weather_repository import WeatherRepository
from app.domains.notifications.repository.notification_repository import NotificationRepository

KST = pytz.timezone("Asia/Seoul")


class WeatherService:
    def __init__(self, db):
        self.db = db
        self.weather_repo = WeatherRepository(db)
        self.notif_repo = NotificationRepository(db)
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    # ------------------------------------------------------------
    # 1) 외부 날씨 API 조회
    # ------------------------------------------------------------
    def fetch_weather(self, lat: float, lng: float):
        try:
            url = (
                f"https://api.openweathermap.org/data/2.5/weather?"
                f"lat={lat}&lon={lng}"
                f"&appid={settings.OPENWEATHER_API_KEY}"
                f"&units=metric&lang=kr"
            )
            res = requests.get(url, timeout=5)

            if res.status_code != 200:
                print("WEATHER API ERROR:", res.text)
                return None

            data = res.json()
            return {
                "condition": data["weather"][0]["main"],
                "condition_ko": data["weather"][0]["description"],
                "temperature_c": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
            }

        except Exception as e:
            print("WEATHER API FAILED:", e)
            return None

    # ------------------------------------------------------------
    # 2) GPT 추천 생성
    # ------------------------------------------------------------
    def generate_advice(self, pet, weekly_minutes, rec_info, weather, trigger_type):
        now = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")

        prompt = f"""
        너는 반려동물 건강·산책 전문가야.
        아래 정보를 기반으로 오늘의 산책 시간대와 산책 시간(분)을 JSON으로 추천해줘.

        반드시 아래 JSON 형식만 출력:
        {{
            "title": "string",
            "message": "string",
            "suggested_time_slots": [
                {{
                    "label": "string",
                    "start_time": "HH:MM",
                    "end_time": "HH:MM"
                }}
            ],
            "suggested_duration_min": int,
            "notes": ["...", "..."]
        }}

        --- 입력 정보 ---
        trigger_type: {trigger_type}
        current_time_kst: {now}

        --- 날씨 ---
        상태: {weather["condition_ko"]}
        기온: {weather["temperature_c"]}℃
        습도: {weather["humidity"]}%

        --- 반려동물 ---
        이름: {pet.name}
        견종: {pet.breed}
        나이: {pet.age}
        체중: {pet.weight}
        질병: {pet.disease}

        --- 최근 활동 ---
        최근 7일 산책 시간: {weekly_minutes}분
        권장 산책: {rec_info}
        """

        res = self.client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.4,
            messages=[
                {"role": "system", "content": "Output JSON only."},
                {"role": "user", "content": prompt},
            ],
        )

        content = res.choices[0].message.content.replace("```json", "").replace("```", "")
        return json.loads(content)

    # ------------------------------------------------------------
    # 3) 최종 알림 message 생성
    # ------------------------------------------------------------
    def build_notification_message(self, pet, weather, advice):
        weather_text = f"오늘 날씨는 {weather['condition_ko']}({weather['temperature_c']}℃)입니다."

        slots = advice.get("suggested_time_slots", [])
        if slots:
            slot = slots[0]
            time_text = f"추천 산책 시간대는 {slot['start_time']}~{slot['end_time']} 입니다."
        else:
            time_text = "오늘은 적절한 산책 시간을 찾기 어려워요."

        note_text = ""
        if advice.get("notes"):
            note_text = f"\n주의사항: {advice['notes'][0]}"

        return f"{weather_text}\n{time_text}{note_text}"

    # ------------------------------------------------------------
    # 4) WEATHER 추천 API
    # ------------------------------------------------------------
    def generate_weather_recommendation(self, request, authorization, body):
        path = request.url.path

        # --- 인증 ---
        if not authorization or not authorization.startswith("Bearer "):
            return error_response(401, "WEATHER_401", "Authorization 필요", path)

        decoded = verify_firebase_token(authorization.split(" ")[1])
        if decoded is None:
            return error_response(401, "WEATHER_401_2", "Invalid token", path)

        user = self.db.query(User).filter(User.firebase_uid == decoded["uid"]).first()
        if not user:
            return error_response(404, "WEATHER_404_1", "사용자 없음", path)

        # --- Pet ---
        pet = self.weather_repo.get_pet(body.pet_id)
        if not pet:
            return error_response(404, "WEATHER_404_2", "반려동물 없음", path)

        # --- Family 권한 체크 ---
        if not self.weather_repo.user_in_family(user.user_id, pet.family_id):
            return error_response(403, "WEATHER_403", "해당 반려동물 접근 불가", path)

        # --- 날씨 ---
        weather = self.fetch_weather(body.lat, body.lng)
        if not weather:
            return error_response(502, "WEATHER_502", "날씨 API 실패", path)

        # --- Walk / Recommendation data ---
        weekly_minutes = self.weather_repo.get_weekly_walk_minutes(pet.pet_id)
        rec = self.weather_repo.get_recommendation(pet.pet_id)

        rec_info = {
            "min_minutes": rec.min_minutes if rec else None,
            "recommended_minutes": rec.recommended_minutes if rec else None,
            "max_minutes": rec.max_minutes if rec else None,
        }

        # --- GPT advice ---
        advice = self.generate_advice(
            pet, weekly_minutes, rec_info, weather, body.trigger_type
        )

        final_message = self.build_notification_message(pet, weather, advice)

        # ------------------------------------------------------------
        # ⭐ target_user_id 설정 (manual vs scheduled)
        # ------------------------------------------------------------
        if body.trigger_type == "scheduled":
            # 가족 전체 Broadcast
            target_user_id = None
        else:
            # manual 요청 → 요청자에게만
            target_user_id = user.user_id

        # ------------------------------------------------------------
        # ⭐ Notification 저장
        # ------------------------------------------------------------
        notif = self.notif_repo.create_notification(
            family_id=pet.family_id,
            target_user_id=target_user_id,
            related_pet_id=pet.pet_id,
            related_user_id=user.user_id,
            notif_type=NotificationType.SYSTEM_WEATHER,
            title=advice["title"],
            message=final_message,
        )

        self.db.commit()

        # ⭐ manual 요청은 자동 읽음 처리
        if target_user_id is not None:
            read = NotificationRead(
                notification_id=notif.notification_id,
                user_id=target_user_id
            )
            self.db.add(read)
            self.db.commit()


        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "status": 200,
                "notification_id": notif.notification_id,
                "title": advice["title"],
                "message": final_message,
                "weather": weather,
                "recommendation": advice,
                "weekly_minutes": weekly_minutes,
                "recommended_info": rec_info,
                "broadcast": (target_user_id is None),  # UI에서 구분 가능
                "timeStamp": datetime.utcnow().isoformat(),
                "path": path,
            },
        )
