from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    firebase_uid = Column(String(128), unique=True, nullable=False)
    sns_id = Column(String(128), unique=False, nullable=False)
    nickname = Column(String(50), nullable=False)

    email = Column(String(100))
    phone = Column(String(20))
    profile_img_url = Column(String(255))

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
