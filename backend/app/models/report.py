from sqlalchemy import Column, String, Boolean, DateTime, Text, Numeric, ForeignKey, CHAR, UniqueConstraint, Integer, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid
from datetime import datetime, timezone
from .base import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(64), nullable=False, index=True)
    source_record_id = Column(String(255), nullable=True, index=True)
    source_hash = Column(CHAR(64), nullable=False)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"), nullable=True)
    report_type = Column(String(64), nullable=False, index=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey("processing_jobs.id"), nullable=True)
    reported_at = Column(DateTime(timezone=True), nullable=True)
    original_text = Column(Text, nullable=False)
    normalized_text = Column(Text, nullable=True)
    language_code = Column(String(32), nullable=True)
    language_confidence = Column(Numeric(6, 5), nullable=True)
    is_mixed_language = Column(Boolean, nullable=False, default=False)
    processing_path = Column(String(64), nullable=True)
    processing_status = Column(String(64), nullable=False, index=True)
    ai_used = Column(Boolean, nullable=False, default=False)
    is_synthetic = Column(Boolean, nullable=False, default=False, index=True)
    pipeline_version = Column(String(64), nullable=False)
    
    # Phase 7, 8, 9 additions
    sif_potential = Column(Boolean, nullable=True)
    sif_score = Column(Numeric(6, 5), nullable=True)
    risk_band = Column(String(32), nullable=True)
    vector_embedding = Column(Vector(768), nullable=True)
    ai_summary = Column(Text, nullable=True)
    ai_solution = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    site = relationship("Site")

    __table_args__ = (
        UniqueConstraint('source', 'source_record_id', name='uq_report_source_id'),
        Index("ix_reports_site_reported", "site_id", "reported_at"),
    )
