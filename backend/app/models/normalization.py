from sqlalchemy import Column, String, Boolean, Text, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from .base import Base

class ReportNormalization(Base):
    __tablename__ = "report_normalizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=False, index=True)
    method = Column(String(64), nullable=False)
    normalized_text = Column(Text, nullable=False)
    normalization_trace = Column(JSONB, nullable=False, default=list)
    is_current = Column(Boolean, nullable=False, default=True)
    confidence = Column(Numeric(5, 4), nullable=True)
    provider = Column(String(64), nullable=True)
    model = Column(String(64), nullable=True)
    prompt_version = Column(String(64), nullable=True)

    report = relationship("Report")
