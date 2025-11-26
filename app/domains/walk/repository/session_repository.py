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

    # =====================================================
    # 진행 중인 산책 가져오기
    # =====================================================
    def get_ongoing_walk_by_pet_id(self, pet_id: int) -> Walk | None:
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

    # =====================================================
    # Walk 세션 생성
    # =====================================================
    def create_walk(
        self,
        pet_id: int,
        user_id: int,
        start_time: datetime,
    ) -> Walk:
        walk = Walk(
            pet_id=pet_id,
            user_id=user_id,
            start_time=start_time,
        )
        self.db.add(walk)
        self.db.flush()   # walk_id 확보
        return walk

    # =====================================================
    # 위치 Tracking Point 저장
    # =====================================================
    def create_tracking_point(
        self,
        walk_id: int,
        latitude: float,
        longitude: float,
        timestamp: datetime,
    ) -> WalkTrackingPoint:
        point = WalkTrackingPoint(
            walk_id=walk_id,
            latitude=latitude,
            longitude=longitude,
            timestamp=timestamp,
        )
        self.db.add(point)
        return point

    # =====================================================
    # walk_id 기준 Walk 조회
    # =====================================================
    def get_walk_by_walk_id(self, walk_id: int) -> Walk | None:
        return (
            self.db.query(Walk)
            .filter(Walk.walk_id == walk_id)
            .first()
        )

    # =====================================================
    # 산책 종료 처리 (last_lat / last_lng 포함)
    # =====================================================
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

        walk.end_time = end_time

        if duration_min is not None:
            walk.duration_min = duration_min

        if distance_km is not None:
            walk.distance_km = distance_km

        # ⭐ 마지막 위치 저장 (6시 자동 날씨 추천에서 사용됨)
        if last_lat is not None:
            walk.last_lat = last_lat
        if last_lng is not None:
            walk.last_lng = last_lng

        # ⭐ route_data 저장은 추후 walk 모델 컬럼 추가 후 활성화
        # if route_data is not None:
        #     walk.route_data = json.dumps(route_data)

        return walk

    # =====================================================
    # 특정 날짜 ActivityStat 조회 or 생성
    # =====================================================
    def get_or_create_activity_stat(
        self,
        pet_id: int,
        stat_date: date,
    ) -> ActivityStat:
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

    # =====================================================
    # ActivityStat 업데이트
    # =====================================================
    def update_activity_stat(
        self,
        stat: ActivityStat,
        distance_km: float,
        duration_min: int,
    ) -> ActivityStat:

        stat.total_walks += 1
        stat.total_distance_km += distance_km
        stat.total_duration_min += duration_min
        
        # 평균 속도 (km/h)
        if stat.total_duration_min > 0:
            total_hours = stat.total_duration_min / 60.0
            stat.avg_speed_kmh = float(stat.total_distance_km) / total_hours
        
        return stat
