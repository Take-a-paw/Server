from pydantic import BaseModel

class HealthFeedbackRequest(BaseModel):
    pet_id: int
