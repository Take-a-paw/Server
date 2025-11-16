from sqlalchemy.orm import Session
from app.models.pet_walk_recommendation import PetWalkRecommendation


class RecommendationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_recommendation_by_pet_id(self, pet_id: int) -> PetWalkRecommendation | None:
        """pet_id로 추천 산책 정보 조회"""
        return (
            self.db.query(PetWalkRecommendation)
            .filter(PetWalkRecommendation.pet_id == pet_id)
            .first()
        )


