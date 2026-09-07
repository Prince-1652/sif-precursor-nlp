from sqlalchemy import Column, String, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from .base import Base

class LSRRulesVersion(Base):
    __tablename__ = "lsr_rules_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version = Column(String(64), nullable=False, index=True)
    rule_code = Column(String(100), nullable=False, index=True)
    positive_terms = Column(JSONB, nullable=False, default=list)
    danger_patterns = Column(JSONB, nullable=False, default=list)
    negative_contexts = Column(JSONB, nullable=False, default=list)
    weight_config = Column(JSONB, nullable=False, default=dict)
