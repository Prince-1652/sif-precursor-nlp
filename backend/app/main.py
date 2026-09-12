from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings

from .api.endpoints import reports, jobs, search, dashboard
from .core.security import verify_api_key, limiter
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from fastapi import Depends, Request

async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    response = JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit exceeded: {exc.detail}"}
    )
    if settings.BACKEND_CORS_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = str(settings.BACKEND_CORS_ORIGINS[0]) if len(settings.BACKEND_CORS_ORIGINS) > 0 else "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="OIL Safety Intelligence API"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-API-Key"],
    )

app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"], dependencies=[Depends(verify_api_key)])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["jobs"], dependencies=[Depends(verify_api_key)])
app.include_router(search.router, prefix="/api/v1/search", tags=["search"], dependencies=[Depends(verify_api_key)])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"], dependencies=[Depends(verify_api_key)])

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from app.models.base import SessionLocal
from app.models.report import Report

logger = logging.getLogger(__name__)

async def dlq_retry_worker():
    while True:
        await asyncio.sleep(60 * 5) # check every 5 minutes
        try:
            db = SessionLocal()
            cutoff = datetime.now(timezone.utc) - timedelta(hours=1.5)
            
            stuck_reports = db.query(Report).filter(
                Report.processing_status == "DLQ",
                Report.updated_at < cutoff
            ).all()
            
            if stuck_reports:
                stuck_ids = [r.id for r in stuck_reports]
                db.query(Report).filter(Report.id.in_(stuck_ids)).update({"processing_status": "READY"}, synchronize_session=False)
                db.commit()
                logger.info(f"DLQ Auto-recovery: Re-queued {len(stuck_ids)} reports.")
                
                from app.services.processing import process_pending_reports
                process_pending_reports()
        except Exception as e:
            logger.error(f"DLQ retry worker error: {e}")
        finally:
            if 'db' in locals():
                db.close()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(dlq_retry_worker())

@app.get("/api/v1/health")
@limiter.limit("60/minute")
def health_check(request: Request):
    return {"status": "ok", "version": "1.0.0"}

@app.get("/api/v1/health/dependencies")
@limiter.limit("10/minute")
def health_dependencies(request: Request):
    from app.models.base import SessionLocal
    from sqlalchemy import text
    
    db = None
    db_status = "ok"
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = "unavailable"
        import logging
        logging.getLogger(__name__).error(f"Database health check failed: {e}")
    finally:
        if db:
            db.close()
        
    ai_status = "ok" if settings.APP_MODE == "offline" or settings.GEMINI_API_KEY else "not_configured"
        
    return {
        "database": db_status,
        "ai_provider": ai_status,
        "app_mode": settings.APP_MODE
    }
