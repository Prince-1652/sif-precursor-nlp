from app.models.base import SessionLocal
from app.models.report import Report
from app.models.job import ProcessingJob
from app.models.audit import AuditEvent
from app.models.normalization import ReportNormalization
from app.models.sif_prediction import SIFPrediction
from app.models.lsr_prediction import LSRPrediction
from app.models.entity import Entity
from app.models.barrier import Barrier
from app.models.evidence import EvidenceItem
from app.models.pattern import Pattern
from app.models.review import ReviewAction

db = SessionLocal()
try:
    db.query(ReviewAction).delete()
    db.query(EvidenceItem).delete()
    db.query(Barrier).delete()
    db.query(Entity).delete()
    db.query(LSRPrediction).delete()
    db.query(SIFPrediction).delete()
    db.query(ReportNormalization).delete()
    db.query(Pattern).delete()
    db.query(AuditEvent).delete()
    from app.models.job import ProcessingAttempt
    db.query(ProcessingAttempt).delete()
    db.query(Report).delete()
    db.query(ProcessingJob).delete()
    db.commit()
    print("All tables cleared successfully.")
except Exception as e:
    db.rollback()
    print(f"Error clearing tables: {e}")
finally:
    db.close()
