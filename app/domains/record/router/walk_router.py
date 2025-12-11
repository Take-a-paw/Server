from fastapi import APIRouter, Header, Request, Depends, Query, Path
from sqlalchemy.orm import Session
from typing import Optional

from app.db import get_db
from app.domains.record.service.walk_service import RecordWalkService
from app.domains.record.service.walk_detail_service import RecordWalkDetailService
from app.domains.record.service.photo_service import RecordPhotoService
from app.domains.record.service.stats_service import ActivityStatsService
from app.domains.record.service.recent_service import RecentActivityService
from app.domains.record.exception import (
    RECORD_WALK_LIST_RESPONSES,
    RECORD_WALK_DETAIL_RESPONSES,
    RECORD_PHOTO_LIST_RESPONSES,
    RECORD_STATS_RESPONSES,
    RECORD_RECENT_RESPONSES,
)
from app.schemas.record.walk_list_schema import WalkListResponse
from app.schemas.record.walk_detail_schema import WalkDetailResponse
from app.schemas.record.photo_list_schema import PhotoListResponse
from app.schemas.record.activity_stats_schema import ActivityStatsResponse
from app.schemas.record.recent_schema import RecentActivitiesResponse


router = APIRouter(
    prefix="/api/v1/record",
    tags=["Record"]
)


@router.get(
    "/walks",
    summary="산책 목록 조회",
    description="특정 반려동물의 산책 목록을 조회합니다. 날짜 범위로 필터링할 수 있습니다.",
    status_code=200,
    response_model=WalkListResponse,
    responses=RECORD_WALK_LIST_RESPONSES,
)
def list_walks(
    request: Request,
    pet_id: int = Query(..., description="반려동물 ID"),
    start_date: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD 형식)"),
    end_date: Optional[str] = Query(None, description="종료 날짜 (YYYY-MM-DD 형식)"),
    authorization: Optional[str] = Header(None, description="Firebase ID 토큰"),
    db: Session = Depends(get_db),
):
    service = RecordWalkService(db)
    return service.list_walks(
        request=request,
        authorization=authorization,
        pet_id=pet_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/walks/{walk_id}",
    summary="산책 상세 조회",
    description="특정 산책의 상세 정보를 조회합니다. 위치 포인트 포함 여부를 선택할 수 있습니다.",
    status_code=200,
    response_model=WalkDetailResponse,
    responses=RECORD_WALK_DETAIL_RESPONSES,
)
def get_walk_detail(
    request: Request,
    walk_id: int = Path(..., description="산책 ID"),
    include_points: Optional[str] = Query(None, description="위치 포인트 포함 여부 (true/false)"),
    authorization: Optional[str] = Header(None, description="Firebase ID 토큰"),
    db: Session = Depends(get_db),
):
    service = RecordWalkDetailService(db)
    return service.get_walk_detail(
        request=request,
        authorization=authorization,
        walk_id=walk_id,
        include_points=include_points,
    )


@router.get(
    "/photos",
    summary="사진첩 조회",
    description="특정 반려동물의 산책 사진 목록을 페이지네이션으로 조회합니다.",
    status_code=200,
    response_model=PhotoListResponse,
    responses=RECORD_PHOTO_LIST_RESPONSES,
)
def list_photos(
    request: Request,
    pet_id: int = Query(..., description="반려동물 ID"),
    start_date: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD 형식)"),
    end_date: Optional[str] = Query(None, description="종료 날짜 (YYYY-MM-DD 형식)"),
    page: int = Query(0, description="페이지 번호 (0부터 시작)", ge=0),
    size: int = Query(20, description="페이지 크기", ge=1, le=100),
    authorization: Optional[str] = Header(None, description="Firebase ID 토큰"),
    db: Session = Depends(get_db),
):
    service = RecordPhotoService(db)
    return service.list_photos(
        request=request,
        authorization=authorization,
        pet_id=pet_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        size=size,
    )


@router.get(
    "/stats",
    summary="활동 시각화 그래프 + 요약",
    description="반려동물의 활동 통계를 조회합니다. 기간별로 그래프 데이터와 요약 정보를 제공합니다.",
    status_code=200,
    response_model=ActivityStatsResponse,
    responses=RECORD_STATS_RESPONSES,
)
def get_activity_stats(
    request: Request,
    pet_id: int = Query(..., description="반려동물 ID"),
    period: str = Query(..., description="조회 기간 (daily, weekly, monthly)"),
    date: Optional[str] = Query(None, description="기준 날짜 (YYYY-MM-DD 형식, daily/weekly용)"),
    start_date: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD 형식, monthly용)"),
    end_date: Optional[str] = Query(None, description="종료 날짜 (YYYY-MM-DD 형식, monthly용)"),
    authorization: Optional[str] = Header(None, description="Firebase ID 토큰"),
    db: Session = Depends(get_db),
):
    # period 변환: daily -> day, weekly -> week, monthly -> month, all -> all
    period_map = {
        "daily": "day",
        "weekly": "week",
        "monthly": "month",
        "all": "all"
    }
    period_normalized = period_map.get(period.lower(), period)
    
    service = ActivityStatsService(db)
    return service.get_stats(
        request=request,
        authorization=authorization,
        pet_id=pet_id,
        period=period_normalized,
        date=date,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/recent",
    summary="최근 활동 조회",
    description="반려동물의 최근 산책 활동을 조회합니다. limit 파라미터로 조회 개수를 지정할 수 있습니다.",
    status_code=200,
    response_model=RecentActivitiesResponse,
    responses=RECORD_RECENT_RESPONSES,
)
def list_recent(
    request: Request,
    pet_id: int = Query(..., description="반려동물 ID"),
    limit: int = Query(20, description="조회할 최대 개수", ge=1, le=100),
    authorization: Optional[str] = Header(None, description="Firebase ID 토큰"),
    db: Session = Depends(get_db),
):
    service = RecentActivityService(db)
    return service.list_recent(
        request=request,
        authorization=authorization,
        pet_id=pet_id,
        limit=limit,
    )
