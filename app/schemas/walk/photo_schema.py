from pydantic import BaseModel, Field
from typing import Optional


class PhotoDetail(BaseModel):
    """사진 상세 정보"""
    photo_id: int = Field(..., description="사진 ID")
    walk_id: int = Field(..., description="산책 ID")
    image_url: str = Field(..., description="이미지 URL")
    uploaded_by: int = Field(..., description="업로드한 사용자 ID")
    caption: Optional[str] = Field(None, description="사진 설명")
    created_at: Optional[str] = Field(None, description="생성 시간 (ISO 형식)")


class PhotoUploadResponse(BaseModel):
    """사진 업로드 응답"""
    success: bool = Field(True, description="성공 여부")
    status: int = Field(201, description="HTTP 상태 코드")
    photo: PhotoDetail = Field(..., description="사진 정보")
    timeStamp: str = Field(..., description="응답 시간 (ISO 형식)")
    path: str = Field(..., description="요청 경로")

