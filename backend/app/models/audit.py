from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from .base import Base

class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey("processing_jobs.id"), nullable=True)
    event_type = Column(String(64), nullable=False)
    actor_type = Column(String(32), nullable=False)
    actor_id = Column(String(255), nullable=True)
    payload = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    report = relationship("Report")
    job = relationship("ProcessingJob")
