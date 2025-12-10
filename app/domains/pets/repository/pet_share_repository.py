from sqlalchemy.orm import Session
from typing import Optional, List

from app.models.pet_share_request import PetShareRequest, RequestStatus
from app.models.family_member import FamilyMember
from app.models.pet import Pet


class PetShareRepository:
    def __init__(self, db: Session):
        self.db = db

    # -------------------------------
    # Pet lookup
    # -------------------------------
    def get_pet_by_search_id(self, pet_search_id: str) -> Optional[Pet]:
        return (
            self.db.query(Pet)
            .filter(Pet.pet_search_id == pet_search_id)
            .first()
        )

    # -------------------------------
    # Family membership
    # -------------------------------
    def is_user_in_family(self, user_id: int, family_id: int) -> bool:
        return (
            self.db.query(FamilyMember)
            .filter(
                FamilyMember.user_id == user_id,
                FamilyMember.family_id == family_id
            )
            .first()
            is not None
        )

    # -------------------------------
    # Share Request
    # -------------------------------
    def create_request(self, pet_id: int, requester_id: int):
        req = PetShareRequest(
            pet_id=pet_id,
            requester_id=requester_id,
            status=RequestStatus.PENDING
        )
        self.db.add(req)
        self.db.flush()
        return req

    def exists_pending_request(self, pet_id: int, requester_id: int) -> bool:
        return (
            self.db.query(PetShareRequest)
            .filter(
                PetShareRequest.pet_id == pet_id,
                PetShareRequest.requester_id == requester_id,
                PetShareRequest.status == RequestStatus.PENDING
            )
            .first()
            is not None
        )

    def reject_other_pending(self, pet_id: int, requester_id: int, exclude_request_id: int):
        """
        동일 사용자/펫의 다른 미처리 요청을 일괄 거절 처리하여
        중복 승인/중복 요청을 방지합니다.
        """
        (
            self.db.query(PetShareRequest)
            .filter(
                PetShareRequest.pet_id == pet_id,
                PetShareRequest.requester_id == requester_id,
                PetShareRequest.status == RequestStatus.PENDING,
                PetShareRequest.request_id != exclude_request_id,
            )
            .update(
                {
                    PetShareRequest.status: RequestStatus.REJECTED,
                },
                synchronize_session=False,
            )
        )

    def get_request_by_id(self, request_id: int) -> Optional[PetShareRequest]:
        return self.db.get(PetShareRequest, request_id)

    def update_request_status(self, req: PetShareRequest, status: RequestStatus):
        req.status = status
        self.db.flush()
        return req
    

    def get_requests_by_user(
        self,
        requester_id: int,
        status: Optional[RequestStatus],
        page: int,
        size: int
    ):
        query = (
            self.db.query(PetShareRequest)
            .filter(PetShareRequest.requester_id == requester_id)
        )

        if status:
            query = query.filter(PetShareRequest.status == status)

        total = query.count()

        items = (
            query.order_by(PetShareRequest.created_at.desc())
            .offset(page * size)
            .limit(size)
            .all()
        )

        return items, total


    # ---------------------------------------------------------
    # ⭐ 추가: 특정 사용자가 보낸 요청 목록
    # ---------------------------------------------------------
    def get_requests_by_requester(self, requester_id: int):
        return (
            self.db.query(PetShareRequest)
            .filter(PetShareRequest.requester_id == requester_id)
            .order_by(PetShareRequest.created_at.desc())
            .all()
        )

    # ---------------------------------------------------------
    # ⭐ 추가: 특정 pet에 대한 모든 요청 목록
    # ---------------------------------------------------------
    def get_requests_by_pet(self, pet_id: int):
        return (
            self.db.query(PetShareRequest)
            .filter(PetShareRequest.pet_id == pet_id)
            .order_by(PetShareRequest.created_at.desc())
            .all()
        )

    # ---------------------------------------------------------
    # ⭐ 추가: 내가 owner인 pet들에 대한 받은 요청 목록 (페이지네이션)
    # ---------------------------------------------------------
    def get_received_requests_by_owner(
        self,
        owner_id: int,
        status: Optional[RequestStatus],
        page: int,
        size: int
    ):
        """
        owner_id가 소유한 pet들에 대해 받은 공유 요청 목록 조회
        """
        query = (
            self.db.query(PetShareRequest)
            .join(Pet, PetShareRequest.pet_id == Pet.pet_id)
            .filter(Pet.owner_id == owner_id)
        )

        if status:
            query = query.filter(PetShareRequest.status == status)

        total = query.count()

        items = (
            query.order_by(PetShareRequest.created_at.desc())
            .offset(page * size)
            .limit(size)
            .all()
        )

        return items, total