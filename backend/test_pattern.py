from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case
from app.models.base import SessionLocal
from app.models.report import Report
from app.models.entity import Entity
from app.models.barrier import Barrier
from app.models.lsr_prediction import LSRPrediction
from app.models.life_saving_rule import LifeSavingRule
from datetime import datetime, timedelta, timezone

def test():
    db = SessionLocal()
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
    
    for row in results:
        print(row)

if __name__ == "__main__":
    test()
