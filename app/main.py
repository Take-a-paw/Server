from fastapi import FastAPI
from app.db import engine
from app.models import Base  # models/__init__.py 에 Base 포함돼 있어야 함

app = FastAPI(
    title="Take a Paw API 🐾",
    version="1.0.0",
    description="Backend API for Take a Paw mobile app"
)

# 🟢 API 테스트용 기본 엔드포인트
@app.get("/")
def root():
    return {"message": "🐾 Take a Paw API is running successfully"}


# 🟢 python -m app.main 로 실행될 때만 동작
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
