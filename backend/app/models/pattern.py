from sqlalchemy import Column, String, Numeric, ForeignKey, Integer, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from .base import Base

class Pattern(Base):
    __tablename__ = "patterns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"), nullable=True)
    activity = Column(String(255), nullable=True)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("life_saving_rules.id"), nullable=True)
    hazard = Column(String(255), nullable=True)
    failed_barrier = Column(String(255), nullable=True)
    frequency = Column(Integer, nullable=False, default=1)
    density = Column(Numeric(5, 4), nullable=True)
    trend = Column(String(64), nullable=True)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)

    site = relationship("Site")
    rule = relationship("LifeSavingRule")

    __table_args__ = (
        Index("ix_patterns_site_period", "site_id", "period_start", "period_end"),
        Index("ix_patterns_rule_period", "rule_id", "period_start", "period_end"),
    )
