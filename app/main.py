from fastapi import FastAPI
import uvicorn
from app.db import engine, Base



app = FastAPI(
    title="Take a Paw API 🐾",
    version="1.0.0",
    description="Backend API for Take a Paw mobile app"
)

@app.get("/")
def root():
    return {"message": "🐾 Take a Paw API is running successfully"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
