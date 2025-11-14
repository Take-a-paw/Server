from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.models.base import Base

class Family(Base):
    __tablename__ = "families"

    family_id = Column(Integer, primary_key=True, autoincrement=True)
    family_name = Column(String(100), nullable=False)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
