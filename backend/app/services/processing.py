import logging
import asyncio
from sqlalchemy.orm import Session
from app.models.report import Report
from app.services.ai_provider import get_ai_provider
from app.models.base import SessionLocal

logger = logging.getLogger(__name__)

async def process_report_async(report_id: str):
    db: Session = SessionLocal()
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report or report.processing_status not in ["READY", "FAILED"]:
            return
            
        report.processing_status = "PROCESSING"
        db.commit()

        provider = get_ai_provider()

        # Step 1: Analyze text to extract structured data
        try:
            analysis = await provider.analyze_safety(report.original_text)
            report.extracted_hazards = analysis.hazards
            report.root_causes = analysis.root_causes
            report.severity_score = analysis.severity_score
            report.sif_potential = analysis.sif_potential
            report.sif_score = analysis.sif_score
            report.risk_band = analysis.risk_band
            report.life_saving_rules = analysis.life_saving_rules
            report.precursors = analysis.precursors
        except Exception as e:
            logger.error(f"Error during LLM analysis for {report_id}: {e}")
            report.processing_status = "FAILED"
            db.commit()
            return
            
        # Step 2: Generate vector embedding
        try:
            embedding = await provider.generate_embedding(report.original_text)
            report.vector_embedding = embedding
        except Exception as e:
            logger.error(f"Error generating embedding for {report_id}: {e}")
            report.processing_status = "FAILED"
            db.commit()
            return

        report.processing_status = "COMPLETED"
        report.ai_used = True
        db.commit()

    except Exception as e:
        logger.error(f"Unhandled error processing report {report_id}: {e}")
        db.rollback()
    finally:
        db.close()

def process_report(report_id: str):
    asyncio.run(process_report_async(report_id))

def process_pending_reports():
    db: Session = SessionLocal()
    try:
        pending_reports = db.query(Report).filter(Report.processing_status == "READY").all()
        report_ids = [str(r.id) for r in pending_reports]
    finally:
        db.close()
        
    for rid in report_ids:
        process_report(rid)
