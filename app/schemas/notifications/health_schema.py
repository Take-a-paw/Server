# app/schemas/notifications/health_schema.py

from pydantic import BaseModel

class HealthFeedbackRequest(BaseModel):
    pet_id: int

class HealthFeedbackResponse(BaseModel):
    success: bool
    status: int
    notification: dict
    advice: dict
    timeStamp: str
    path: str
