# app/domains/notifications/service/notification_service.py

from datetime import datetime
from typing import Optional

from fastapi import Request
from sqlalchemy.orm import Session

from app.core.firebase import verify_firebase_token
from app.core.error_handler import error_response

from app.models.user import User
from app.models.notification_reads import NotificationRead
from app.models.pet_share_request import PetShareRequest, RequestStatus

from app.domains.notifications.repository.notification_repository import (
    NotificationRepository,
)
from app.schemas.notifications.notification_schema import NotificationListResponse


# 한국어 라벨 매핑 (UI용)
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

    # -----------------------------
    # GET /api/v1/notifications
    # -----------------------------
    def get_notifications(
        self,
        request: Request,
        firebase_token: Optional[str],
        pet_id: Optional[int],
        notif_type: Optional[str],
        page: int,
        size: int,
    ):
        try:
            # 1) Authorization 검증
            if not firebase_token:
                return error_response(
                    status=401,
                    code="NOTIF_LIST_401_1",
                    reason="Authorization 헤더가 필요합니다.",
                    path=request.url.path,
                )

            decoded = verify_firebase_token(firebase_token)
            if decoded is None:
                return error_response(
                    status=401,
                    code="NOTIF_LIST_401_2",
                    reason="유효하지 않거나 만료된 Firebase ID Token입니다. 다시 로그인해주세요.",
                    path=request.url.path,
                )

            firebase_uid = decoded["uid"]

            # 2) 사용자 조회
            user = (
                self.db.query(User)
                .filter(User.firebase_uid == firebase_uid)
                .first()
            )
            if not user:
                return error_response(
                    status=404,
                    code="NOTIF_LIST_404_1",
                    reason="해당 사용자를 찾을 수 없습니다.",
                    path=request.url.path,
                )

            # 3) page / size 검증
            if page < 0 or size <= 0:
                return error_response(
                    status=400,
                    code="NOTIF_LIST_400_2",
                    reason="page와 size는 숫자여야 합니다.",
                    path=request.url.path,
                )

            # 4) 알림 조회
            items, total = self.repo.get_notifications(
                user_id=user.user_id,
                pet_id=pet_id,
                notif_type=notif_type,
                page=page,
                size=size,
            )

            if items is None and total == "INVALID_TYPE":
                return error_response(
                    status=400,
                    code="NOTIF_LIST_400_1",
                    reason="알림 타입이 올바르지 않습니다.",
                    path=request.url.path,
                )

            # 5) 응답 리스트 조립
            results = []

            for notif in items:
                type_str = notif.type.value

                # 읽음 여부 (NotificationRead에 존재?)
                is_read_by_me = (
                    self.db.query(NotificationRead)
                    .filter(
                        NotificationRead.notification_id == notif.notification_id,
                        NotificationRead.user_id == user.user_id,
                    )
                    .first()
                    is not None
                )

                # 가족 수
                family_count = (
                    self.repo.get_family_member_count(notif.family_id)
                    if notif.family_id
                    else 1
                )
                read_count = self.repo.get_read_count(notif.notification_id)
                unread_count = max(family_count - read_count, 0)

                # UI 라벨
                display_type_label = f"[{TYPE_LABELS.get(type_str, type_str)}]"
                display_time = (
                    notif.created_at.strftime("%H:%M")
                    if notif.created_at
                    else ""
                )
                display_read_text = f"{read_count}명 읽음"

                # 말풍선 정보
                sender_profile_img_url = (
                    notif.related_user.profile_img_url
                    if notif.related_user
                    else None
                )
                sender_nickname = (
                    notif.related_user.nickname if notif.related_user else None
                )
                is_me = notif.related_user_id == user.user_id

                # REQUEST 알림이면 공유 요청 ID 붙이기 ⭐
                share_request_id = notif.related_request_id

                results.append(
                    {
                        "notification_id": notif.notification_id,
                        "type": type_str,
                        "title": notif.title,
                        "family_id": notif.family_id,
                        "target_user_id": notif.target_user_id,
                        "related_pet": notif.related_pet,
                        "related_user": notif.related_user,
                        "related_lat": notif.related_lat,
                        "related_lng": notif.related_lng,
                        "share_request_id": share_request_id,  # ⭐ 추가됨
                        "is_read_by_me": is_read_by_me,
                        "read_count": read_count,
                        "unread_count": unread_count,
                        "created_at": notif.created_at,
                        "display_type_label": display_type_label,
                        "display_time": display_time,
                        "display_read_text": display_read_text,
                        "sender_profile_img_url": sender_profile_img_url,
                        "sender_nickname": sender_nickname,
                        "is_me": is_me,
                    }
                )

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
            return error_response(
                status=500,
                code="NOTIF_LIST_500_1",
                reason="알림 목록을 조회하는 중 오류가 발생했습니다.",
                path=request.url.path,
            )
