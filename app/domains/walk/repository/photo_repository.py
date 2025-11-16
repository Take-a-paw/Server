from sqlalchemy.orm import Session
from typing import Optional
from app.models.photo import Photo


class PhotoRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_photo(
        self,
        walk_id: int,
        image_url: str,
        uploaded_by: int,
        caption: Optional[str] = None,
    ) -> Photo:
        """사진 생성"""
        photo = Photo(
            walk_id=walk_id,
            image_url=image_url,
            uploaded_by=uploaded_by,
            caption=caption,
        )
        self.db.add(photo)
        return photo

