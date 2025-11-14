from sqlalchemy import Column, Integer, DateTime, DECIMAL, ForeignKey
from sqlalchemy.sql import func
from app.models.base import Base

class PetWalkGoal(Base):
    __tablename__ = "pet_walk_goals"

    goal_id = Column(Integer, primary_key=True, autoincrement=True)
    pet_id = Column(Integer, ForeignKey("pets.pet_id"), nullable=False, unique=True)

    target_walks = Column(Integer, nullable=False)
    target_minutes = Column(Integer, nullable=False)
    target_distance_km = Column(DECIMAL(5, 2), nullable=False)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
