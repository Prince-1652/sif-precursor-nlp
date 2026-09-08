from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class ReportBase(BaseModel):
    source: str
    source_record_id: Optional[str] = None
    report_type: str
    reported_at: Optional[datetime] = None
    original_text: str = Field(..., max_length=50000)
    site_id: Optional[UUID] = None

class ReportCreate(ReportBase):
    pass

class ReportResponse(ReportBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    processing_status: str
    is_mixed_language: bool
    ai_used: bool
    pipeline_version: str
    created_at: datetime
    updated_at: datetime
    
    extracted_hazards: Optional[list[str]] = None
    root_causes: Optional[list[str]] = None
    severity_score: Optional[int] = None
    sif_potential: Optional[bool] = None
    sif_score: Optional[float] = None
    risk_band: Optional[str] = None
    life_saving_rules: Optional[list[str]] = None
    precursors: Optional[list[str]] = None
