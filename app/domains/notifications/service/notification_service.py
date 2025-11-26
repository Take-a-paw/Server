# app/domains/notifications/service/notification_service.py

from datetime import datetime
from typing import Optional

from fastapi import Request
from sqlalchemy.orm import Session

from app.core.firebase import verify_firebase_token
from app.core.error_handler import error_response

from app.models.user import User
from app.models.notification_reads import NotificationRead

from app.domains.notifications.repository.notification_repository import NotificationRepository
from app.schemas.notifications.notification_schema import NotificationListResponse

TYPE_LABELS = {
    "REQUEST": "승인 요청",
    "INVITE_ACCEPTED": "요청 수락",
    "INVITE_REJECTED": "요청 거절",
    "ACTIVITY_START": "산책 시작",
    "ACTIVITY_END": "산책 종료",
    "FAMILY_ROLE_CHANGED": "역할 변경",
    "PET_UPDATE": "반려동물 정보 수정",
    "SYSTEM_RANKING": "산책왕 알림",
    "SYSTEM_WEATHER": "날씨 기반 산책 추천",
    "SYSTEM_REMINDER": "산책 알림",
    "SYSTEM_HEALTH": "건강 피드백",
    "SOS": "긴급 알림",
    "SOS_RESOLVED": "긴급 상황 해제",
}


class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = NotificationRepository(db)

    # ============================
    # 📌 알림 목록
    # ============================
    def get_notifications(self, request: Request, firebase_token, pet_id, notif_type, page, size):
        try:
            # 인증
            if not firebase_token:
                return error_response(401, "NOTIF_401", "Authorization 필요", request.url.path)

            decoded = verify_firebase_token(firebase_token)
            if decoded is None:
                return error_response(401, "NOTIF_401_2", "Firebase 토큰 오류", request.url.path)

            user = (
                self.db.query(User)
                .filter(User.firebase_uid == decoded["uid"])
                .first()
            )
            if not user:
                return error_response(404, "NOTIF_404_1", "사용자 없음", request.url.path)

            items, total = self.repo.get_notifications(
                user_id=user.user_id,
                pet_id=pet_id,
                notif_type=notif_type,
                page=page,
                size=size,
            )

            if items is None and total == "INVALID_TYPE":
                return error_response(400, "NOTIF_400", "알림 타입 오류", request.url.path)

            results = []

            for notif in items:
                type_str = notif.type.value
                sender_id = notif.related_user_id
                is_me = sender_id == user.user_id

                # 내가 읽었는지
                is_read_by_me = (
                    self.db.query(NotificationRead)
                    .filter(
                        NotificationRead.notification_id == notif.notification_id,
                        NotificationRead.user_id == user.user_id,
                    )
                    .first()
                    is not None
                )

                family_count = self.repo.get_family_member_count(notif.family_id)
                read_count = self.repo.get_read_count(notif.notification_id)
                unread_count = max(family_count - read_count, 0)

                results.append({
                    "notification_id": notif.notification_id,
                    "type": type_str,
                    "title": notif.title,
                    "message": notif.message,
                    "family_id": notif.family_id,
                    "target_user_id": notif.target_user_id,
                    "related_pet": notif.related_pet,
                    "related_user": notif.related_user,
                    "related_lat": notif.related_lat,
                    "related_lng": notif.related_lng,
                    "share_request_id": notif.related_request_id,
                    "is_read_by_me": is_read_by_me,
                    "read_count": read_count,
                    "unread_count": unread_count,
                    "created_at": notif.created_at,
                    "display_type_label": f"[{TYPE_LABELS.get(type_str, type_str)}]",
                    "display_time": notif.created_at.strftime("%H:%M"),
                    "display_read_text": f"{read_count}명 읽음",
                    "sender_profile_img_url": notif.related_user.profile_img_url if notif.related_user else None,
                    "sender_nickname": notif.related_user.nickname if notif.related_user else None,
                    "is_me": is_me,
                })

            return NotificationListResponse(
                success=True,
                status=200,
                notifications=results,
                page=page,
                size=size,
                total_count=total,
                timeStamp=datetime.utcnow().isoformat(),
                path=request.url.path,
            )

        except Exception as e:
            print("ERROR IN NotificationService.get_notifications():", e)
            self.db.rollback()
            return error_response(500, "NOTIF_500", "알림 조회 오류", request.url.path)

    # ============================
    # 📌 읽음 처리
    # ============================
    def mark_read(self, request, firebase_token, notification_id):
        path = request.url.path

        if not firebase_token:
            return error_response(401, "NOTIF_READ_401_1", "Authorization 필요", path)

        decoded = verify_firebase_token(firebase_token)
        if decoded is None:
            return error_response(401, "NOTIF_READ_401_2", "토큰 오류", path)

        user = (
            self.db.query(User)
            .filter(User.firebase_uid == decoded["uid"])
            .first()
        )
        if not user:
            return error_response(404, "NOTIF_READ_404_1", "사용자 없음", path)

        notif = self.repo.get_notification_by_id(notification_id)
        if not notif:
            return error_response(404, "NOTIF_READ_404_2", "알림 없음", path)

        existing = (
            self.db.query(NotificationRead)
            .filter(
                NotificationRead.notification_id == notification_id,
                NotificationRead.user_id == user.user_id,
            )
            .first()
        )
        if existing:
            return {
                "success": True,
                "status": 200,
                "message": "이미 읽음",
                "notification_id": notification_id,
                "timeStamp": datetime.utcnow().isoformat(),
                "path": path
            }

        try:
            read = NotificationRead(
                notification_id=notification_id,
                user_id=user.user_id,
                read_at=datetime.utcnow(),
            )
            self.db.add(read)
            self.db.commit()

        except Exception as e:
            print("NOTIFICATION_READ_ERROR:", e)
            self.db.rollback()
            return error_response(500, "NOTIF_READ_500_1", "읽음 처리 오류", path)

        return {
            "success": True,
            "status": 200,
            "message": "읽음 처리 완료",
            "notification_id": notification_id,
            "timeStamp": datetime.utcnow().isoformat(),
            "path": path
        }
