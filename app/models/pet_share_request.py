from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from app.models.base import Base
import enum

class RequestStatus(enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class PetShareRequest(Base):
    __tablename__ = "pet_share_requests"

    request_id = Column(Integer, primary_key=True, autoincrement=True)
    pet_id = Column(Integer, ForeignKey("pets.pet_id"), nullable=False)
    requester_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    status = Column(Enum(RequestStatus), default=RequestStatus.PENDING)
    message = Column(String(255))

    created_at = Column(DateTime, default=func.now())
    responded_at = Column(DateTime)
