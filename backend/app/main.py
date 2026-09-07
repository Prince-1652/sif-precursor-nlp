from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings

from .api.endpoints import reports, jobs, search, dashboard

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="OIL Safety Intelligence API"
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["jobs"])
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}

@app.get("/api/v1/health/dependencies")
def health_dependencies():
    from app.models.base import SessionLocal
    from sqlalchemy import text
    
    db_status = "ok"
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"failed: {e}"
    finally:
        db.close()
        
    ai_status = "ok" if settings.APP_MODE == "offline" or settings.GEMINI_API_KEY else "not_configured"
        
    return {
        "database": db_status,
        "ai_provider": ai_status,
        "app_mode": settings.APP_MODE
    }
