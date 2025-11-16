from pydantic import BaseModel, Field
from typing import List, Optional


class UploadedBy(BaseModel):
    user_id: int
    nickname: Optional[str]


class PhotoListItem(BaseModel):
    photo_id: int
    walk_id: int
    image_url: str
    uploaded_by: UploadedBy
    caption: Optional[str]
    walk_date: Optional[str]
    walk_start_time: Optional[str]
    created_at: Optional[str]


class PhotoListResponse(BaseModel):
    success: bool = Field(True)
    status: int = Field(200)
    pet_id: int
    photos: List[PhotoListItem] = Field(default_factory=list)
    page: int
    size: int
    total_count: int
    timeStamp: str
    path: str
