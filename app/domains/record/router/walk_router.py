from fastapi import APIRouter, Header, Request, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.db import get_db
from app.domains.record.service.walk_service import RecordWalkService
from app.domains.record.service.walk_detail_service import RecordWalkDetailService
from app.domains.record.service.photo_service import RecordPhotoService
from app.domains.record.service.stats_service import ActivityStatsService
from app.domains.record.service.recent_service import RecentActivityService
from app.schemas.error_schema import ErrorResponse
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
    status_code=200,
    response_model=WalkListResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
def list_walks(
    request: Request,
    pet_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    authorization: Optional[str] = Header(None),
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
    status_code=200,
    response_model=WalkDetailResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
def get_walk_detail(
    request: Request,
    walk_id: int,
    include_points: Optional[str] = None,
    authorization: Optional[str] = Header(None),
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
    status_code=200,
    response_model=PhotoListResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
def list_photos(
    request: Request,
    pet_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 0,
    size: int = 20,
    authorization: Optional[str] = Header(None),
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
    status_code=200,
    response_model=ActivityStatsResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
def get_activity_stats(
    request: Request,
    pet_id: int,
    period: str,
    date: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    service = ActivityStatsService(db)
    return service.get_stats(
        request=request,
        authorization=authorization,
        pet_id=pet_id,
        period=period,
        date=date,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/recent",
    summary="최근 활동 조회 (최대 3개)",
    status_code=200,
    response_model=RecentActivitiesResponse,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
def list_recent(
    request: Request,
    pet_id: int,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    service = RecentActivityService(db)
    return service.list_recent(
        request=request,
        authorization=authorization,
        pet_id=pet_id,
        limit=3,
    )
