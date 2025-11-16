from sqlalchemy.orm import Session
from typing import Optional
from app.models.pet_walk_goal import PetWalkGoal


class GoalRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_goal_by_pet_id(self, pet_id: int) -> PetWalkGoal | None:
        """pet_id로 목표 산책량 조회"""
        return (
            self.db.query(PetWalkGoal)
            .filter(PetWalkGoal.pet_id == pet_id)
            .first()
        )

    def get_goal_by_goal_id(self, goal_id: int) -> PetWalkGoal | None:
        """goal_id로 목표 산책량 조회"""
        return (
            self.db.query(PetWalkGoal)
            .filter(PetWalkGoal.goal_id == goal_id)
            .first()
        )

    def create_goal(
        self,
        pet_id: int,
        target_walks: int,
        target_minutes: int,
        target_distance_km: float,
    ) -> PetWalkGoal:
        """목표 산책량 생성"""
        goal = PetWalkGoal(
            pet_id=pet_id,
            target_walks=target_walks,
            target_minutes=target_minutes,
            target_distance_km=target_distance_km,
        )
        self.db.add(goal)
        return goal

    def update_goal(
        self,
        goal: PetWalkGoal,
        target_walks: int,
        target_minutes: int,
        target_distance_km: float,
    ) -> PetWalkGoal:
        """목표 산책량 업데이트"""
        goal.target_walks = target_walks
        goal.target_minutes = target_minutes
        goal.target_distance_km = target_distance_km
        return goal

    def partial_update_goal(
        self,
        goal: PetWalkGoal,
        target_walks: Optional[int] = None,
        target_minutes: Optional[int] = None,
        target_distance_km: Optional[float] = None,
    ) -> PetWalkGoal:
        """목표 산책량 부분 업데이트"""
        if target_walks is not None:
            goal.target_walks = target_walks
        if target_minutes is not None:
            goal.target_minutes = target_minutes
        if target_distance_km is not None:
            goal.target_distance_km = target_distance_km
        return goal

