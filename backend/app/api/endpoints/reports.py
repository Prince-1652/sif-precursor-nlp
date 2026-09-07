from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from uuid import UUID
from app.api import deps
from app.schemas.job import ProcessingJobResponse
from app.schemas.report import ReportResponse, ReportCreate
from app.models.report import Report
from app.services.ingestion import process_csv_upload
from app.services.processing import process_report, process_pending_reports

router = APIRouter()

@router.post("/upload", response_model=ProcessingJobResponse)
async def upload_csv(background_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(deps.get_db)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    content = await file.read()
    job = process_csv_upload(db, content, file.filename)
    
    # Trigger background processing for the newly ingested reports
    background_tasks.add_task(process_pending_reports)
    
    return job

@router.post("/manual", response_model=ReportResponse)
async def create_manual_report(report_in: ReportCreate, background_tasks: BackgroundTasks, db: Session = Depends(deps.get_db)):
    from app.services.ingestion import generate_source_hash
    import uuid
    
    report = Report(
        source=report_in.source,
        source_record_id=report_in.source_record_id or f"MANUAL-{uuid.uuid4().hex[:6]}",
        source_hash=generate_source_hash(report_in.original_text),
        report_type=report_in.report_type,
        original_text=report_in.original_text,
        processing_status="READY",
        pipeline_version="1.0.0"
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    
    background_tasks.add_task(process_report, str(report.id))
    return report

@router.post("/{report_id}/process")
async def trigger_report_processing(report_id: UUID, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_report, str(report_id))
    return {"message": "Processing started in background"}

@router.get("", response_model=List[ReportResponse])
def get_reports(db: Session = Depends(deps.get_db), limit: int = 50):
    return db.query(Report).order_by(Report.created_at.desc()).limit(limit).all()

@router.get("/stats")
def get_stats(db: Session = Depends(deps.get_db)) -> Dict[str, Any]:
    total_reports = db.query(Report).count()
    completed_reports = db.query(Report).filter(Report.processing_status == 'COMPLETED').count()
    high_severity = db.query(Report).filter(Report.severity_score >= 4).count()
    return {
        "total_reports": total_reports,
        "completed_reports": completed_reports,
        "high_severity": high_severity
    }
