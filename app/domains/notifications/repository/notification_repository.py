from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models.notification import Notification, NotificationType
from app.models.notification_reads import NotificationRead
from app.models.family_member import FamilyMember


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    # ============================
    # 📌 알림 조회
    # ============================
    def get_notifications(
        self,
        user_id: int,
        pet_id: int | None,
        notif_type: str | None,
        page: int,
        size: int
    ):
        # 사용자가 속한 family_id 목록
        family_ids = (
            self.db.query(FamilyMember.family_id)
            .filter(FamilyMember.user_id == user_id)
            .subquery()
        )

        query = (
            self.db.query(Notification)
            .options(
                joinedload(Notification.related_user),
                joinedload(Notification.related_pet),
            )
            .filter(
                # 개인 알림
                (Notification.target_user_id == user_id)
                |
                # 가족 공용 알림
                ((Notification.target_user_id.is_(None)) &
                 (Notification.family_id.in_(family_ids)))
            )
        )

        # pet 필터
        if pet_id is not None:
            query = query.filter(Notification.related_pet_id == pet_id)

        # type 필터
        if notif_type is not None:
            try:
                t_enum = NotificationType[notif_type]
                query = query.filter(Notification.type == t_enum)
            except KeyError:
                return None, "INVALID_TYPE"

        # 채팅 스타일 → 오래된 순
        query = query.order_by(Notification.created_at.asc())

        total = query.count()
        items = query.offset(page * size).limit(size).all()

        return items, total

    # ============================
    # 📌 가족 인원수
    # ============================
    def get_family_member_count(self, family_id: int) -> int:
        return (
            self.db.query(func.count(FamilyMember.user_id))
            .filter(FamilyMember.family_id == family_id)
            .scalar()
        )

    # ============================
    # 📌 읽은 사람 수
    # ============================
    def get_read_count(self, notification_id: int) -> int:
        return (
            self.db.query(NotificationRead.user_id)
            .filter(NotificationRead.notification_id == notification_id)
            .distinct()
            .count()
        )

    # ============================
    # 📌 읽음 처리
    # ============================
    def mark_as_read(self, notification_id: int, user_id: int):
        existing = (
            self.db.query(NotificationRead)
            .filter(
                NotificationRead.notification_id == notification_id,
                NotificationRead.user_id == user_id
            )
            .first()
        )

        if existing:
            return "ALREADY_READ"

        new_row = NotificationRead(
            notification_id=notification_id,
            user_id=user_id
        )
        self.db.add(new_row)
        self.db.commit()
        return "OK"

    # ============================
    # 📌 단일 조회
    # ============================
    def get_notification_by_id(self, notification_id: int):
        return (
            self.db.query(Notification)
            .filter(Notification.notification_id == notification_id)
            .first()
        )

    # ============================
    # 📌 알림 생성
    # ============================
    def create_notification(
        self,
        family_id: int,
        related_pet_id: int,
        related_user_id: int,
        notif_type: NotificationType,
        title: str,
        message: str,
        target_user_id=None,   # ⭐ None이면 Broadcast
    ):
        notif = Notification(
            family_id=family_id,
            target_user_id=target_user_id,
            related_pet_id=related_pet_id,
            related_user_id=related_user_id,
            type=notif_type,
            title=title,
            message=message,
        )
        self.db.add(notif)
        self.db.flush()  # notification_id 확보

        # ⭐ 개인 알림인 경우 즉시 읽음 처리
        if target_user_id is not None:
            read = NotificationRead(
                notification_id=notif.notification_id,
                user_id=target_user_id
            )
            self.db.add(read)

        return notif
