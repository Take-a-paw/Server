import firebase_admin
from firebase_admin import credentials, auth, storage
from app.core.config import settings
import os
from datetime import datetime

# Firebase Credential 파일 경로 로드
cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)

# 앱 초기화 (중복 초기화 방지)
if not firebase_admin._apps:
    firebase_app = firebase_admin.initialize_app(cred)

# Firebase Storage 버킷 이름 (환경 변수에서 가져오거나 기본값 사용)
STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET", "")


def verify_firebase_token(id_token: str):
    try:
        decoded = auth.verify_id_token(id_token)
        return decoded
    except Exception:
        return None


def upload_file_to_storage(
    file_content: bytes,
    file_name: str,
    content_type: str = "image/jpeg",
    folder: str = "walk_photos"
) -> str:
    """
    Firebase Storage에 파일 업로드
    
    Returns:
        str: 업로드된 파일의 public URL
    """
    try:
        bucket = storage.bucket(STORAGE_BUCKET) if STORAGE_BUCKET else storage.bucket()
        
        # 파일 경로 생성
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        blob_path = f"{folder}/{timestamp}_{file_name}"
        
        # Blob 생성 및 업로드
        blob = bucket.blob(blob_path)
        blob.upload_from_string(file_content, content_type=content_type)
        
        # Public URL 반환
        blob.make_public()
        return blob.public_url
        
    except Exception as e:
        print(f"STORAGE_UPLOAD_ERROR: {e}")
        raise Exception("STORAGE_UPLOAD_FAILED")
