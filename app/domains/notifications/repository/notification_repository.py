from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.notification import Notification
from app.models.notification_read import NotificationRead
from app.models.pet import Pet
from app.models.user import User
from app.models.family_member import FamilyMember


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    # 전체 family 구성원 수 조회
    def get_family_member_count(self, family_id: int):
        return (
            self.db.query(FamilyMember)
            .filter(FamilyMember.family_id == family_id)
            .count()
        )

    # 알림 읽음 count 조회
    def get_read_count(self, notification_id: int):
        return (
            self.db.query(NotificationRead)
            .filter(NotificationRead.notification_id == notification_id)
            .count()
        )

    # notifications 조회 (페이징 + type + pet_id)
    def get_notifications(self, user_id: int, pet_id: int | None, type_val: str | None, page: int, size: int):
        query = (
            self.db.query(Notification)
            .filter(Notification.target_user_id == user_id)
        )

        if pet_id:
            query = query.filter(Notification.related_pet_id == pet_id)

        if type_val:
            query = query.filter(Notification.type == type_val)

        total_count = query.count()

        notifications = (
            query.order_by(Notification.created_at.desc())
            .offset(page * size)
            .limit(size)
            .all()
        )

        return notifications, total_count

    # 관련 객체 조회
    def get_related_pet(self, pet_id: int):
        return self.db.query(Pet).filter(Pet.pet_id == pet_id).first()

    def get_related_user(self, user_id: int):
        return self.db.query(User).filter(User.user_id == user_id).first()
