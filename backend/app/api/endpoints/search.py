from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api import deps
from app.schemas.report import ReportResponse
from app.models.report import Report
from app.services.ai_provider import get_ai_provider

router = APIRouter()

@router.get("", response_model=List[ReportResponse])
async def search_reports(query: str, limit: int = 10, db: Session = Depends(deps.get_db)):
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
        
    try:
        # Generate embedding for the search query
        provider = get_ai_provider()
        query_embedding = await provider.generate_embedding(query)
        
        # Perform cosine distance search
        # pgvector uses cosine_distance
        reports = db.query(Report).filter(
            Report.vector_embedding.is_not(None)
        ).order_by(
            Report.vector_embedding.cosine_distance(query_embedding)
        ).limit(limit).all()
        
        return reports
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
