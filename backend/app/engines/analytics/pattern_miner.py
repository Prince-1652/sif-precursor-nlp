from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case
from datetime import datetime, timedelta, timezone
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
    now = datetime.now(timezone.utc)
    thirty_days_ago = now - timedelta(days=30)
    sixty_days_ago = now - timedelta(days=60)
    
    results = db.query(
        Report.site_id,
        Report.report_type,
        LifeSavingRule.rule_code,
        Barrier.barrier_name,
        func.count(Barrier.id).label('frequency'),
        func.sum(case((Report.created_at >= thirty_days_ago, 1), else_=0)).label('recent_freq'),
        func.sum(case(((Report.created_at >= sixty_days_ago) & (Report.created_at < thirty_days_ago), 1), else_=0)).label('past_freq')
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
    for site_id, rep_type, rule, barrier, freq, recent_freq, past_freq in results:
        # Calculate real period-over-period trend
        if past_freq == 0:
            trend = "RISING" if recent_freq > 0 else "STABLE"
        else:
            change = (recent_freq - past_freq) / past_freq
            if change > 0.1:
                trend = "RISING"
            elif change < -0.1:
                trend = "FALLING"
            else:
                trend = "STABLE"
                
        patterns.append({
            "site_id": str(site_id) if site_id else "ALL",
            "activity": rep_type,
            "lsr_rule": rule,
            "failed_barrier": barrier,
            "frequency": freq,
            "trend": trend
        })
        
    return patterns
