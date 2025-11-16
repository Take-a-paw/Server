from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, date
from typing import Optional
import json

from app.models.walk import Walk
from app.models.walk_tracking_point import WalkTrackingPoint
from app.models.activity_stat import ActivityStat


class SessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_ongoing_walk_by_pet_id(self, pet_id: int) -> Walk | None:
        """pet_id로 진행 중인 산책 조회 (end_time이 null인 것)"""
        return (
            self.db.query(Walk)
            .filter(
                and_(
                    Walk.pet_id == pet_id,
                    Walk.end_time.is_(None)
                )
            )
            .first()
        )

    def create_walk(
        self,
        pet_id: int,
        user_id: int,
        start_time: datetime,
    ) -> Walk:
        """새로운 산책 세션 생성"""
        walk = Walk(
            pet_id=pet_id,
            user_id=user_id,
            start_time=start_time,
        )
        self.db.add(walk)
        self.db.flush()  # walk_id를 얻기 위해 flush
        return walk

    def create_tracking_point(
        self,
        walk_id: int,
        latitude: float,
        longitude: float,
        timestamp: datetime,
    ) -> WalkTrackingPoint:
        """산책 시작 지점의 tracking point 생성"""
        point = WalkTrackingPoint(
            walk_id=walk_id,
            latitude=latitude,
            longitude=longitude,
            timestamp=timestamp,
        )
        self.db.add(point)
        return point

    def get_walk_by_walk_id(self, walk_id: int) -> Walk | None:
        """walk_id로 산책 세션 조회"""
        return (
            self.db.query(Walk)
            .filter(Walk.walk_id == walk_id)
            .first()
        )

    def end_walk(
        self,
        walk: Walk,
        end_time: datetime,
        duration_min: Optional[int] = None,
        distance_km: Optional[float] = None,
        last_lat: Optional[float] = None,
        last_lng: Optional[float] = None,
        route_data: Optional[dict] = None,
    ) -> Walk:
        """산책 세션 종료"""
        walk.end_time = end_time
        if duration_min is not None:
            walk.duration_min = duration_min
        if distance_km is not None:
            walk.distance_km = distance_km
        # route_data는 JSON 문자열로 저장 (Walk 모델에 route_data 컬럼이 있다고 가정)
        # 실제로는 마이그레이션으로 route_data 컬럼을 추가해야 함
        # 일단 주석 처리하고, 나중에 추가 가능하도록 함
        # if route_data is not None:
        #     walk.route_data = json.dumps(route_data)
        return walk

    def get_or_create_activity_stat(
        self,
        pet_id: int,
        stat_date: date,
    ) -> ActivityStat:
        """활동 통계 조회 또는 생성"""
        stat = (
            self.db.query(ActivityStat)
            .filter(
                and_(
                    ActivityStat.pet_id == pet_id,
                    ActivityStat.date == stat_date
                )
            )
            .first()
        )
        
        if not stat:
            stat = ActivityStat(
                pet_id=pet_id,
                date=stat_date,
                total_walks=0,
                total_distance_km=0,
                total_duration_min=0,
            )
            self.db.add(stat)
            self.db.flush()
        
        return stat

    def update_activity_stat(
        self,
        stat: ActivityStat,
        distance_km: float,
        duration_min: int,
    ) -> ActivityStat:
        """활동 통계 업데이트"""
        stat.total_walks += 1
        stat.total_distance_km += distance_km
        stat.total_duration_min += duration_min
        
        # 평균 속도 계산 (km/h)
        if stat.total_duration_min > 0:
            total_hours = stat.total_duration_min / 60.0
            stat.avg_speed_kmh = float(stat.total_distance_km) / total_hours
        
        return stat

