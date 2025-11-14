from sqlalchemy import Column, Integer, DECIMAL, DateTime, String, ForeignKey
from sqlalchemy.sql import func
from app.models.base import Base

class Walk(Base):
    __tablename__ = "walks"

    walk_id = Column(Integer, primary_key=True, autoincrement=True)
    pet_id = Column(Integer, ForeignKey("pets.pet_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    duration_min = Column(Integer)
    distance_km = Column(DECIMAL(5, 2))
    calories = Column(DECIMAL(6, 2))

    weather_status = Column(String(50))
    weather_temp_c = Column(DECIMAL(4, 1))

    created_at = Column(DateTime, default=func.now())
