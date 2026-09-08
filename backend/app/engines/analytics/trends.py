from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from app.models.report import Report
from app.models.sif_prediction import SIFPrediction

def compute_trends(db: Session):
    now = datetime.now(timezone.utc)
    thirty_days_ago = now - timedelta(days=30)
    sixty_days_ago = now - timedelta(days=60)
    
    # Volume trend
    recent_volume = db.query(Report).filter(Report.created_at >= thirty_days_ago).count()
    past_volume = db.query(Report).filter(Report.created_at >= sixty_days_ago, Report.created_at < thirty_days_ago).count()
    
    if past_volume == 0:
        volume_trend = "RISING" if recent_volume > 0 else "STABLE"
    else:
        change = (recent_volume - past_volume) / past_volume
        if change > 0.1:
            volume_trend = "RISING"
        elif change < -0.1:
            volume_trend = "FALLING"
        else:
            volume_trend = "STABLE"
            
    # SIF trend
    recent_sifs = db.query(SIFPrediction).join(Report).filter(Report.created_at >= thirty_days_ago, SIFPrediction.is_current == True, SIFPrediction.sif_potential == True).count()
    past_sifs = db.query(SIFPrediction).join(Report).filter(Report.created_at >= sixty_days_ago, Report.created_at < thirty_days_ago, SIFPrediction.is_current == True, SIFPrediction.sif_potential == True).count()
    
    recent_sif_rate = (recent_sifs / recent_volume) if recent_volume > 0 else 0
    past_sif_rate = (past_sifs / past_volume) if past_volume > 0 else 0
    
    if past_sif_rate == 0:
        sif_trend = "RISING" if recent_sif_rate > 0 else "STABLE"
    else:
        change = (recent_sif_rate - past_sif_rate) / past_sif_rate
        if change > 0.1:
            sif_trend = "RISING"
        elif change < -0.1:
            sif_trend = "FALLING"
        else:
            sif_trend = "STABLE"

    # Trending terms
    from app.models.entity import Entity
    from sqlalchemy import desc
    
    recent_terms = db.query(Entity.value, func.count(Entity.id).label('count')) \
        .join(Report, Entity.report_id == Report.id) \
        .filter(Report.created_at >= thirty_days_ago) \
        .filter(Entity.entity_type.in_(['HAZARD', 'ACTIVITY'])) \
        .group_by(Entity.value) \
        .order_by(desc('count')) \
        .limit(5) \
        .all()
        
    trending_terms = [t[0] for t in recent_terms]

    return {
        "sif_trend": sif_trend,
        "volume_trend": volume_trend,
        "trending_terms": trending_terms
    }
