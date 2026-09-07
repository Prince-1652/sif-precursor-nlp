from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class ProcessingJobBase(BaseModel):
    job_type: str
    status: str
    total_records: int
    processed_records: int
    failed_records: int
    ai_records: int

class ProcessingJobCreate(BaseModel):
    job_type: str
    total_records: int
    idempotency_key: Optional[str] = None

class ProcessingJobResponse(ProcessingJobBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    idempotency_key: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_summary: Optional[Dict[str, Any]] = None
    created_at: datetime
