from sqlalchemy import Column, Integer, DECIMAL, DateTime, ForeignKey
from app.models.base import Base

class WalkTrackingPoint(Base):
    __tablename__ = "walk_tracking_points"

    point_id = Column(Integer, primary_key=True, autoincrement=True)
    walk_id = Column(Integer, ForeignKey("walks.walk_id"), nullable=False)

    latitude = Column(DECIMAL(10, 7), nullable=False)
    longitude = Column(DECIMAL(10, 7), nullable=False)
    timestamp = Column(DateTime, nullable=False)
