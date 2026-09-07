from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from app.models.report import Report
from app.models.sif_prediction import SIFPrediction
from app.models.lsr_prediction import LSRPrediction
from app.models.life_saving_rule import LifeSavingRule

def compute_summary(db: Session) -> dict:
    total_reports = db.query(Report).filter(
        Report.processing_status.in_([
            "COMPLETED", 
            "AUTO_ACCEPTED_LOW_RISK", 
            "AUTO_ACCEPTED_HIGH_CONFIDENCE"
        ])
    ).count()
    
    sif_count = db.query(SIFPrediction).filter(SIFPrediction.is_current == True, SIFPrediction.sif_potential == True).count()
    sif_percentage = (sif_count / total_reports) if total_reports > 0 else 0.0
    
    high_risk_count = db.query(SIFPrediction).filter(SIFPrediction.is_current == True, SIFPrediction.risk_band == "HIGH").count()
    
    review_count = db.query(Report).filter(Report.processing_status.in_(["REVIEW_REQUIRED", "REVIEW_RECOMMENDED"])).count()
    
    ai_processed_count = db.query(Report).filter(Report.ai_used == True).count()
    
    from app.models.site import Site
    total_sites = db.query(Site).count()
    
    # LSR distribution
    lsr_results = db.query(LifeSavingRule.rule_code, func.count(LSRPrediction.id)).join(LSRPrediction, LifeSavingRule.id == LSRPrediction.rule_id).filter(LSRPrediction.matched == True, LSRPrediction.is_current == True).group_by(LifeSavingRule.rule_code).all()
    lsr_distribution = {row[0]: row[1] for row in lsr_results}

    return {
        "total_reports": total_reports,
        "sif_count": sif_count,
        "sif_percentage": sif_percentage,
        "high_risk_count": high_risk_count,
        "review_count": review_count,
        "ai_processed_count": ai_processed_count,
        "total_sites": total_sites,
        "lsr_distribution": lsr_distribution,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }
