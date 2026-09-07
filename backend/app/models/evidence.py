from sqlalchemy import Column, String, Numeric, ForeignKey, Integer, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from .base import Base

class EvidenceItem(Base):
    __tablename__ = "evidence_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=False)
    source_type = Column(String(64), nullable=False)
    start_offset = Column(Integer, nullable=False)
    end_offset = Column(Integer, nullable=False)
    phrase = Column(Text, nullable=False)
    concept = Column(String(100), nullable=False)
    engine = Column(String(64), nullable=False)
    weight = Column(Numeric(5, 4), nullable=True)

    report = relationship("Report")

    __table_args__ = (
        Index("ix_evidence_items_report", "report_id"),
    )
