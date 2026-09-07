from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.report import Report
from app.models.entity import Entity
from app.models.barrier import Barrier
from app.models.lsr_prediction import LSRPrediction
from app.models.life_saving_rule import LifeSavingRule

def mine_patterns(db: Session) -> list[dict]:
    """
    Find recurring (site, activity, LSR, failed_barrier) combos.
    For simplicity, we find the most frequent failed barriers grouped by rule.
    """
    # A robust pattern miner would use more complex SQL or dataframes.
    # We will do a basic grouped query: Failed Barriers joined with LSR Predictions
    
    results = db.query(
        Report.site_id,
        Report.report_type,
        LifeSavingRule.rule_code,
        Barrier.barrier_name,
        func.count(Barrier.id).label('frequency')
    ).select_from(Report).join(
        LSRPrediction, LSRPrediction.report_id == Report.id
    ).join(
        LifeSavingRule, LifeSavingRule.id == LSRPrediction.rule_id
    ).join(
        Barrier, Barrier.report_id == Report.id
    ).filter(
        Barrier.status == "FAILED",
        LSRPrediction.matched == True,
        LSRPrediction.is_current == True
    ).group_by(
        Report.site_id,
        Report.report_type,
        LifeSavingRule.rule_code,
        Barrier.barrier_name
    ).order_by(
        desc('frequency')
    ).limit(10).all()
    
    patterns = []
    for site_id, rep_type, rule, barrier, freq in results:
        patterns.append({
            "site_id": str(site_id) if site_id else "ALL",
            "activity": rep_type,
            "lsr_rule": rule,
            "failed_barrier": barrier,
            "frequency": freq,
            "trend": "STABLE"
        })
        
    return patterns
