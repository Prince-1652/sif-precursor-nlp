# Import all models here for Alembic to detect them automatically
from app.models.base import Base

from app.models.site import Site
from app.models.report import Report
from app.models.job import ProcessingJob, ProcessingAttempt
from app.models.audit import AuditEvent
from app.models.life_saving_rule import LifeSavingRule
from app.models.lsr_rules_version import LSRRulesVersion
from app.models.normalization import ReportNormalization
from app.models.sif_prediction import SIFPrediction
from app.models.lsr_prediction import LSRPrediction
from app.models.entity import Entity
from app.models.barrier import Barrier
from app.models.evidence import EvidenceItem
from app.models.pattern import Pattern
from app.models.review import ReviewAction
