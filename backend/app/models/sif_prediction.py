from sqlalchemy import Column, String, Boolean, Numeric, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from .base import Base

class SIFPrediction(Base):
    __tablename__ = "sif_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=False)
    is_current = Column(Boolean, nullable=False, default=True)
    sif_potential = Column(Boolean, nullable=False)
    score = Column(Numeric(5, 4), nullable=False)
    confidence = Column(Numeric(5, 4), nullable=False)
    risk_band = Column(String(32), nullable=False)
    engine_name = Column(String(64), nullable=False)
    engine_version = Column(String(64), nullable=False)
    method = Column(String(64), nullable=False)
    evidence_summary = Column(JSONB, nullable=False, default=list)

    report = relationship("Report")

    __table_args__ = (
        Index("ix_sif_predictions_report_current", "report_id", "is_current"),
        Index("ix_sif_predictions_potential_created", "sif_potential", "is_current"),
    )
