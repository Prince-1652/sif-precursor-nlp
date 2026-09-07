from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings

from .api.endpoints import reports, jobs, search

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

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}
