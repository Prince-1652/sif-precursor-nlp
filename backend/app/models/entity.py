from sqlalchemy import Column, String, Numeric, ForeignKey, Integer, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from .base import Base

class Entity(Base):
    __tablename__ = "entities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=False)
    entity_type = Column(String(64), nullable=False)
    value = Column(String(255), nullable=False)
    normalized_value = Column(String(255), nullable=True)
    source_start = Column(Integer, nullable=True)
    source_end = Column(Integer, nullable=True)
    confidence = Column(Numeric(5, 4), nullable=True)
    extraction_method = Column(String(64), nullable=False)

    report = relationship("Report")

    __table_args__ = (
        Index("ix_entities_report_type", "report_id", "entity_type"),
    )
