from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey
from sqlalchemy.sql import func
from app.models.base import Base

class PetWalkRecommendation(Base):
    __tablename__ = "pet_walk_recommendations"

    rec_id = Column(Integer, primary_key=True, autoincrement=True)
    pet_id = Column(Integer, ForeignKey("pets.pet_id"), nullable=False, unique=True)

    min_walks = Column(Integer, nullable=False)
    min_minutes = Column(Integer, nullable=False)
    min_distance_km = Column(DECIMAL(5, 2), nullable=False)

    recommended_walks = Column(Integer, nullable=False)
    recommended_minutes = Column(Integer, nullable=False)
    recommended_distance_km = Column(DECIMAL(5, 2), nullable=False)

    max_walks = Column(Integer, nullable=False)
    max_minutes = Column(Integer, nullable=False)
    max_distance_km = Column(DECIMAL(5, 2), nullable=False)

    generated_by = Column(String(50), default="LLM")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
