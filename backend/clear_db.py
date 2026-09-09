import sys
import os

# Add backend directory to path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.base import Base, engine
# Import all models to ensure they are registered with Base.metadata
from app.models.report import Report
from app.models.sif_prediction import SIFPrediction
from app.models.lsr_prediction import LSRPrediction
from app.models.entity import Entity
from app.models.barrier import Barrier
from app.models.evidence import EvidenceItem
from app.models.normalization import ReportNormalization
from app.models.audit import AuditEvent
from app.models.job import ProcessingJob, ProcessingAttempt
from app.models.site import Site
from app.models.life_saving_rule import LifeSavingRule

def clear_db():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Recreating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Database cleared and recreated successfully!")

if __name__ == "__main__":
    clear_db()
