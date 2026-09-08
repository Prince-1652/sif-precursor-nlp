from sqlalchemy import Column, String, Boolean, Numeric, ForeignKey, Index, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from .base import Base

class LSRPrediction(Base):
    __tablename__ = "lsr_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=False)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("life_saving_rules.id"), nullable=False)
    is_current = Column(Boolean, nullable=False, default=True)
    matched = Column(Boolean, nullable=False)
    score = Column(Numeric(6, 5), nullable=False)
    confidence = Column(Numeric(6, 5), nullable=False)
    method = Column(String(64), nullable=False)
    matched_phrases = Column(JSONB, nullable=False, default=list)
    engine_version = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    report = relationship("Report")
    rule = relationship("LifeSavingRule")

    __table_args__ = (
        Index("ix_lsr_predictions_report_current", "report_id", "is_current"),
        Index("ix_lsr_predictions_rule_current", "rule_id", "is_current"),
    )
