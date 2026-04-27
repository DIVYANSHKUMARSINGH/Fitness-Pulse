from fastapi import FastAPI
from app.core.config import settings
from app.core.database import engine, Base
from app.api.endpoints import health, users, workouts

# Import all models so Base.metadata knows about them
from app.models import user, workout  # noqa: F401

# Create all database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="FitnessPulse API — Track your fitness journey with data-driven insights."
)

# Wire up all routers under the /api/v1 prefix
app.include_router(health.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(workouts.router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "Welcome to FitnessPulse API!"}
