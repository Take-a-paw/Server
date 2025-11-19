from sqlalchemy.orm import Session
from app.models.notification import Notification

class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_notifications_by_pet(self, pet_id: int, limit: int = 50, offset: int = 0):
        return (
            self.db.query(Notification)
            .filter(Notification.related_pet_id == pet_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
