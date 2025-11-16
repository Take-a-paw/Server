from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from typing import Tuple

from app.models.walk import Walk


class TodayRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_today_walks_stats(
        self, pet_id: int, today_start: datetime, today_end: datetime
    ) -> Tuple[int, int, float, int, bool]:
        """
        오늘 날짜 기준으로 산책 통계를 조회합니다.
        
        Returns:
            Tuple[int, int, float, int, bool]:
            - total_walks: 완료된 산책 횟수
            - total_duration_min: 총 산책 시간 (분)
            - total_distance_km: 총 이동 거리 (km)
            - current_walk_order: 현재 산책 순서
            - has_ongoing_walk: 진행 중인 산책이 있는지
        """
        # 오늘 시작된 모든 산책 조회 (완료 여부와 관계없이, start_time으로 정렬)
        all_today_walks = (
            self.db.query(Walk)
            .filter(
                and_(
                    Walk.pet_id == pet_id,
                    Walk.start_time >= today_start,
                    Walk.start_time < today_end
                )
            )
            .order_by(Walk.start_time.asc())
            .all()
        )

        # 완료된 산책만 필터링 (end_time이 있는 것)
        completed_walks = [w for w in all_today_walks if w.end_time is not None]
        
        # 진행 중인 산책 확인 (end_time이 null이고 오늘 시작된 것)
        ongoing_walks = [w for w in all_today_walks if w.end_time is None]
        has_ongoing_walk = len(ongoing_walks) > 0

        # 완료된 산책 통계 계산
        total_walks = len(completed_walks)
        total_duration_min = sum(w.duration_min or 0 for w in completed_walks)
        total_distance_km = sum(float(w.distance_km or 0) for w in completed_walks)

        # 현재 산책 순서 계산
        if has_ongoing_walk:
            # 진행 중인 산책이 있으면, 그 산책의 순서를 반환
            ongoing_walk = ongoing_walks[0]  # 가장 먼저 시작된 진행 중인 산책
            current_walk_order = all_today_walks.index(ongoing_walk) + 1
        else:
            # 진행 중인 산책이 없으면 다음 산책 순서 (완료된 산책 수 + 1)
            current_walk_order = total_walks + 1

        return total_walks, total_duration_min, total_distance_km, current_walk_order, has_ongoing_walk

