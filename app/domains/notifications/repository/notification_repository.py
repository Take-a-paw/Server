# app/domains/notifications/repository/notification_repository.py

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models.notification import Notification, NotificationType
from app.models.notification_reads import NotificationRead
from app.models.family_member import FamilyMember


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_notifications(
        self,
        user_id: int,
        pet_id: int | None,
        notif_type: str | None,
        page: int,
        size: int
    ):
        query = (
            self.db.query(Notification)
            .options(
                joinedload(Notification.related_user),
                joinedload(Notification.related_pet),
            )
        )

        # 사용자가 속한 family만 조회
        query = query.join(
            FamilyMember,
            FamilyMember.family_id == Notification.family_id
        ).filter(FamilyMember.user_id == user_id)

        # pet 필터
        if pet_id is not None:
            query = query.filter(Notification.related_pet_id == pet_id)

        # type 필터
        if notif_type is not None:
            try:
                notif_type_enum = NotificationType[notif_type]
                query = query.filter(Notification.type == notif_type_enum)
            except KeyError:
                return None, "INVALID_TYPE"

        # ⭐ 변경된 정렬: created_at ASC (카톡 스타일)
        query = query.order_by(Notification.created_at.asc())

        # total count
        total_count = query.count()

        # paging
        items = query.offset(page * size).limit(size).all()

        return items, total_count

    # ------------------------------
    # read/unread 계산 관련 추가 메서드들
    # ------------------------------
    def get_family_member_count(self, family_id: int) -> int:
        return (
            self.db.query(func.count(FamilyMember.user_id))
            .filter(FamilyMember.family_id == family_id)
            .scalar()
        )

    def get_read_count(self, notification_id: int) -> int:
        return (
            self.db.query(func.count(NotificationRead.user_id))
            .filter(NotificationRead.notification_id == notification_id)
            .scalar()
        )

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
