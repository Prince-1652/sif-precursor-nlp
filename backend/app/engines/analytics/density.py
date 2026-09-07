from sqlalchemy.orm import Session
from sqlalchemy import func, Integer
from app.models.report import Report
from app.core.config import settings

def compute_site_density(db: Session) -> list[dict]:
    # Group by report.site_id, compute density
    results = db.query(Report.site_id, func.count(Report.id), func.sum(func.cast(Report.sif_potential, Integer))).filter(Report.processing_status.in_(["AUTO_ACCEPTED_HIGH_CONFIDENCE", "AUTO_ACCEPTED_LOW_RISK", "REVIEW_RECOMMENDED"]), Report.site_id.isnot(None)).group_by(Report.site_id).all()
    
    densities = []
    for site_id, total, sif_sum in results:
        sif_count = int(sif_sum) if sif_sum else 0
        density = sif_count / total if total > 0 else 0.0
        densities.append({
            "site_id": site_id,
            "valid_reports": total,
            "sif_reports": sif_count,
            "density": density,
            "low_sample": total < settings.MIN_SAMPLE_SIZE
        })
        
    return densities
