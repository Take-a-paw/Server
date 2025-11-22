from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_
from app.models.notification import Notification, NotificationType
from app.models.notification_reads import NotificationRead
from app.models.user import User
from app.models.pet import Pet
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

        # 1) 사용자가 속한 family만 가져오기
        query = query.join(
            FamilyMember,
            FamilyMember.family_id == Notification.family_id
        ).filter(FamilyMember.user_id == user_id)

        # 2) pet_id filter
        if pet_id is not None:
            query = query.filter(Notification.related_pet_id == pet_id)

        # 3) type filter
        if notif_type is not None:
            try:
                notif_type_enum = NotificationType[notif_type]
                query = query.filter(Notification.type == notif_type_enum)
            except KeyError:
                return None, "INVALID_TYPE"

        # 4) 정렬
        query = query.order_by(Notification.created_at.desc())

        # 5) total count
        total_count = query.count()

        # 6) 페이징
        items = (
            query.offset(page * size)
            .limit(size)
            .all()
        )

        return items, total_count

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
