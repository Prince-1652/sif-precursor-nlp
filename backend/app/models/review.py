from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from .base import Base

class ReviewAction(Base):
    __tablename__ = "review_actions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=False)
    reviewer_id = Column(String(255), nullable=True) # Could be user ID or name
    decision = Column(String(64), nullable=False) # CONFIRM, REJECT, EDIT
    original_prediction_id = Column(UUID(as_uuid=True), nullable=True)
    corrected_lsr_ids = Column(JSONB, nullable=True)
    corrected_entities = Column(JSONB, nullable=True)
    comment = Column(Text, nullable=True)
    
    from datetime import datetime, timezone
    from sqlalchemy import DateTime
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    report = relationship("Report")
