# app/routers/ranking_router.py

from fastapi import APIRouter, Request, Header, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.domains.walk.service.ranking_service import RankingService
from app.schemas.walk.walk_ranking_schema import WalkRankingResponse
from app.schemas.error_schema import ErrorResponse

router = APIRouter(prefix="/api/v1/walk", tags=["Walk"])


@router.get(
    "/ranking",
    summary="가족 산책 랭킹 조회",
    response_model=WalkRankingResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    }
)
def get_ranking(
    request: Request,
    family_id: int,
    period: str = "weekly",
    pet_id: int | None = None,
    authorization: str | None = Header(None),
    db: Session = Depends(get_db),
):
    service = RankingService(db)
    return service.get_ranking(
        request=request,
        authorization=authorization,
        family_id=family_id,
        period=period,
        pet_id=pet_id
    )
