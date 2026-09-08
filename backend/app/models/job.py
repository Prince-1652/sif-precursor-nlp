from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from .base import Base

class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_type = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False, index=True)
    idempotency_key = Column(String(255), nullable=True)
    total_records = Column(Integer, nullable=False, default=0)
    processed_records = Column(Integer, nullable=False, default=0)
    failed_records = Column(Integer, nullable=False, default=0)
    ai_records = Column(Integer, nullable=False, default=0)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_summary = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True, nullable=False)

    attempts = relationship("ProcessingAttempt", back_populates="job")

class ProcessingAttempt(Base):
    __tablename__ = "processing_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("processing_jobs.id"), nullable=True)
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=True, index=True)
    stage = Column(String(64), nullable=False, index=True)
    attempt_number = Column(Integer, nullable=False, default=1)
    status = Column(String(32), nullable=False)
    duration_ms = Column(Integer, nullable=True)
    error_code = Column(String(128), nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True, nullable=False)

    job = relationship("ProcessingJob", back_populates="attempts")
    report = relationship("Report")
