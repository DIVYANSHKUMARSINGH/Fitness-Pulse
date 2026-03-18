from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="FitnessPulse API"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to FitnessPulse API!"}
