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
from app.core.security import limiter
from fastapi import Request

router = APIRouter()

@router.post("/upload", response_model=ProcessingJobResponse)
async def upload_csv(background_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(deps.get_db)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    MAX_SIZE = 10 * 1024 * 1024  # 10 MB
    chunks = []
    total_size = 0
    
    while True:
        chunk = await file.read(8192)
        if not chunk:
            break
        total_size += len(chunk)
        if total_size > MAX_SIZE:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")
        chunks.append(chunk)
    
    content = b"".join(chunks)
        
    job = process_csv_upload(db, content, file.filename)
    
    # Trigger background processing for the newly ingested reports
    background_tasks.add_task(process_pending_reports)
    
    return job

@router.post("/manual", response_model=ReportResponse)
async def create_manual_report(report_in: ReportCreate, background_tasks: BackgroundTasks, db: Session = Depends(deps.get_db)):
    from app.services.ingestion import generate_source_hash
    import uuid
    
    source_hash = generate_source_hash(report_in.original_text)
    
    # Deduplication: If text was already processed (from CSV or Manual), return the existing report instantly!
    existing_report = db.query(Report).filter(Report.source_hash == source_hash).first()
    if existing_report:
        return existing_report
    
    report = Report(
        source=report_in.source,
        source_record_id=report_in.source_record_id or f"MANUAL-{uuid.uuid4().hex[:6]}",
        source_hash=source_hash,
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

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class ReviewDecision(str, Enum):
    CONFIRM = "CONFIRM"
    REJECT = "REJECT"
    EDIT = "EDIT"

class ReviewActionRequest(BaseModel):
    decision: ReviewDecision
    corrected_lsr_ids: Optional[List[str]] = None
    corrected_entities: Optional[List[dict]] = None
    comment: Optional[str] = None
    original_prediction_id: Optional[UUID] = None

@router.post("/{report_id}/review")
def submit_review(report_id: UUID, review_in: ReviewActionRequest, db: Session = Depends(deps.get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    from app.models.review import ReviewAction
    from app.models.audit import AuditEvent
    
    review = ReviewAction(
        report_id=report.id,
        reviewer_id="human_reviewer", # hardcoded for now until auth is added
        decision=review_in.decision.value,
        original_prediction_id=review_in.original_prediction_id,
        corrected_lsr_ids=review_in.corrected_lsr_ids,
        corrected_entities=review_in.corrected_entities,
        comment=review_in.comment
    )
    db.add(review)
    
    # Update report status
    if review_in.decision.value == "CONFIRM":
        report.processing_status = "COMPLETED"
    elif review_in.decision.value == "EDIT":
        report.processing_status = "COMPLETED_WITH_EDITS"
    elif review_in.decision.value == "REJECT":
        report.processing_status = "REJECTED"
        
    # Audit trail
    db.add(AuditEvent(
        report_id=report.id,
        job_id=report.job_id,
        event_type="REVIEWED",
        actor_type="HUMAN",
        actor_id="human_reviewer",
        payload={"decision": review_in.decision.value, "comment": review_in.comment}
    ))
    
    db.commit()
    return {"status": "success", "decision": review_in.decision}

@router.get("", response_model=List[ReportResponse])
def get_reports(db: Session = Depends(deps.get_db), limit: int = 50):
    return db.query(Report).order_by(Report.created_at.desc()).limit(limit).all()

@router.get("/{report_id}")
def get_report_details(report_id: UUID, db: Session = Depends(deps.get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    from app.models.sif_prediction import SIFPrediction
    from app.models.lsr_prediction import LSRPrediction
    from app.models.entity import Entity
    from app.models.barrier import Barrier
    from app.models.evidence import EvidenceItem
    from app.models.normalization import ReportNormalization
    from app.models.review import ReviewAction
    
    sif = db.query(SIFPrediction).filter(SIFPrediction.report_id == str(report.id), SIFPrediction.is_current == True).first()
    lsrs = db.query(LSRPrediction).filter(LSRPrediction.report_id == str(report.id), LSRPrediction.is_current == True).all()
    entities = db.query(Entity).filter(Entity.report_id == str(report.id)).all()
    barriers = db.query(Barrier).filter(Barrier.report_id == str(report.id)).all()
    evidence = db.query(EvidenceItem).filter(EvidenceItem.report_id == str(report.id)).all()
    normalizations = db.query(ReportNormalization).filter(ReportNormalization.report_id == str(report.id)).all()
    reviews = db.query(ReviewAction).filter(ReviewAction.report_id == str(report.id)).order_by(ReviewAction.created_at.desc()).all()
    
    lsr_data = []
    for lsr in lsrs:
        lsr_data.append({
            "id": lsr.id,
            "rule_id": lsr.rule.rule_code if lsr.rule else str(lsr.rule_id),
            "confidence": float(lsr.confidence) if lsr.confidence else 0.0,
            "score": float(lsr.score) if lsr.score else 0.0,
            "matched_phrases": lsr.matched_phrases
        })

    return {
        "report": {
            "id": report.id,
            "original_text": report.original_text,
            "normalized_text": report.normalized_text,
            "processing_status": report.processing_status,
            "processing_path": report.processing_path,
            "sif_potential": report.sif_potential,
            "sif_score": report.sif_score,
            "risk_band": report.risk_band,
            "ai_used": report.ai_used,
            "language_code": report.language_code
        },
        "sif_prediction": sif,
        "lsr_predictions": lsr_data,
        "entities": entities,
        "barriers": barriers,
        "evidence": evidence,
        "normalizations": normalizations,
        "reviews": reviews
    }

from pydantic import BaseModel
from typing import Optional

class AnalyzeRequest(BaseModel):
    original_text: str = Field(..., max_length=50000)
    report_type: Optional[str] = None
    site_id: Optional[str] = None
    source_record_id: Optional[str] = None
    reported_at: Optional[str] = None

@router.post("/analyze")
@limiter.limit("20/minute")
async def analyze_report_sync(request: Request, req: AnalyzeRequest):
    # Synchronously run the pipeline for the given text without DB saving
    from app.engines.preprocessing.pipeline import run_preprocessing
    from app.engines.language_gate.detector import LanguageDetector
    from app.engines.language_gate.gate import decide_routing, LanguageGateDecision
    from app.providers import get_ai_provider
    from app.engines.sif import sif_engine
    from app.engines.lsr import lsr_engine
    from app.engines.entities import entity_engine
    from app.engines.decision import decision_engine
    import asyncio
    
    prep_result = run_preprocessing(req.original_text)
    if not prep_result.is_valid:
        return {"error": "Invalid text", "details": prep_result.validation_errors}
        
    detector = LanguageDetector()
    detection = detector.detect(prep_result.normalized_text)
    decision = decide_routing(detection, len(prep_result.normalized_text))
    
    ai_used = False
    norm_text = prep_result.normalized_text
    
    if decision not in [LanguageGateDecision.INSUFFICIENT_TEXT, LanguageGateDecision.REVIEW_REQUIRED, LanguageGateDecision.DETERMINISTIC_ENGLISH]:
        ai_used = True
        provider = get_ai_provider()
        norm_res = await provider.normalize_text(norm_text)
        norm_text = norm_res.normalized_text
        
    sif_result, lsr_results, entity_results = await asyncio.gather(
        sif_engine.analyze(norm_text),
        lsr_engine.analyze(norm_text),
        entity_engine.extract(norm_text)
    )
    
    review_state, contradictions, updated_sif_result = decision_engine.orchestrate(sif_result, lsr_results, entity_results)
    
    return {
        "processing_path": decision.value,
        "ai_used": ai_used,
        "normalized_text": norm_text,
        "normalization": {
            "normalization_trace": prep_result.normalization_trace
        },
        "sif_prediction": updated_sif_result,
        "lsr_predictions": lsr_results,
        "entities": entity_results,
        "review_state": review_state,
        "contradictions": contradictions
    }
