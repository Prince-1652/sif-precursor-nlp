from sqlalchemy import Column, String, Numeric, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from .base import Base

class Barrier(Base):
    __tablename__ = "barriers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=False)
    barrier_name = Column(String(255), nullable=False)
    status = Column(String(64), nullable=False) # FAILED, SUCCESSFUL, UNKNOWN
    evidence_text = Column(Text, nullable=True)
    confidence = Column(Numeric(5, 4), nullable=True)

    report = relationship("Report")

    __table_args__ = (
        Index("ix_barriers_report_status", "report_id", "status"),
        Index("ix_barriers_name_status", "barrier_name", "status"),
    )
