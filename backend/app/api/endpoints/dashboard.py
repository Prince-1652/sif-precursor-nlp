from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.engines.analytics import compute_summary, compute_site_density, compute_trends, mine_patterns

router = APIRouter()

@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    summary = compute_summary(db)
    trends = compute_trends(db)
    summary.update(trends)
    return summary

@router.get("/sites")
def get_dashboard_sites(db: Session = Depends(get_db)):
    sites = compute_site_density(db)
    return {"sites": sites}

@router.get("/patterns")
def get_dashboard_patterns(db: Session = Depends(get_db)):
    patterns = mine_patterns(db)
    return {"patterns": patterns}
