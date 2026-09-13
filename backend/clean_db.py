from app.models.base import SessionLocal, Base
from sqlalchemy import MetaData
import contextlib

def clean_db():
    db = SessionLocal()
    try:
        # Delete from tables in correct order to respect foreign keys
        from app.models.entity import Entity
        from app.models.barrier import Barrier
        from app.models.lsr_prediction import LSRPrediction
        from app.models.audit import AuditEvent
        from app.models.report import Report
        from app.models.job import ProcessingJob, ProcessingAttempt
        from app.models.normalization import ReportNormalization
        from app.models.sif_prediction import SIFPrediction
        from app.models.evidence import EvidenceItem
        from app.models.review import ReviewAction
        
        db.query(Entity).delete()
        db.query(Barrier).delete()
        db.query(LSRPrediction).delete()
        db.query(SIFPrediction).delete()
        db.query(EvidenceItem).delete()
        db.query(AuditEvent).delete()
        db.query(ProcessingAttempt).delete()
        db.query(ReportNormalization).delete()
        db.query(ReviewAction).delete()
        db.query(Report).delete()
        db.query(ProcessingJob).delete()
        
        db.commit()
        print("Database cleaned. All reports and related data deleted.")
    except Exception as e:
        print(f"Failed to clean DB: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clean_db()
