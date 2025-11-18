from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)

    # Firebase 고유 UID
    firebase_uid = Column(String(128), unique=True, nullable=False)

    # SNS 제공자 (구 enum)
    sns = Column(
        Enum("google", "apple", "kakao", "email", name="sns_enum"),
        nullable=False
    )

    # 프로필 기본 정보
    nickname = Column(String(50), nullable=False)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)

    profile_img_url = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<User id={self.user_id}, uid={self.firebase_uid}, sns={self.sns}>"
