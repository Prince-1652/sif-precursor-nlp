import logging
import asyncio
from sqlalchemy.orm import Session
from app.models.report import Report
from app.providers import get_ai_provider
from app.models.base import SessionLocal
from app.engines.sif import sif_engine
from app.engines.lsr import lsr_engine
from app.engines.entities import entity_engine
from app.engines.decision import decision_engine
from app.models.evidence import EvidenceItem

logger = logging.getLogger(__name__)

from contextlib import contextmanager
import time

@contextmanager
def stage_timer(db: Session, job_id: str, report_id: str, stage_name: str):
    start_time = time.time()
    from app.models.job import ProcessingAttempt
    attempt = ProcessingAttempt(
        job_id=job_id,
        report_id=report_id,
        stage=stage_name,
        status="RUNNING"
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    
    try:
        yield attempt
        attempt.status = "COMPLETED"
        attempt.duration_ms = int((time.time() - start_time) * 1000)
        db.commit()
    except Exception as e:
        attempt.status = "FAILED"
        attempt.error_message = str(e)
        attempt.duration_ms = int((time.time() - start_time) * 1000)
        db.commit()
        raise

async def process_report_async(report_id: str):
    db: Session = SessionLocal()
    
    # helper for audit events
    def audit(event_type, payload):
        from app.models.audit import AuditEvent
        db.add(AuditEvent(
            report_id=report_id,
            job_id=report.job_id if 'report' in locals() and report else None,
            event_type=event_type,
            actor_type="SYSTEM",
            payload=payload
        ))
    
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report or report.processing_status not in ["READY", "FAILED"]:
            return
            
        report.processing_status = "PROCESSING"
        db.commit()

        # Phase 1.3: Enforce Idempotency (Clear old records)
        from app.models.normalization import ReportNormalization
        from app.models.sif_prediction import SIFPrediction
        from app.models.lsr_prediction import LSRPrediction
        from app.models.entity import Entity
        from app.models.barrier import Barrier
        from app.models.evidence import EvidenceItem
        
        # Soft delete versioned predictions
        db.query(ReportNormalization).filter(ReportNormalization.report_id == report_id).update({"is_current": False})
        db.query(SIFPrediction).filter(SIFPrediction.report_id == report_id).update({"is_current": False})
        db.query(LSRPrediction).filter(LSRPrediction.report_id == report_id).update({"is_current": False})
        
        # Hard delete unversioned child records to prevent duplication on retries
        db.query(Entity).filter(Entity.report_id == report_id).delete()
        db.query(Barrier).filter(Barrier.report_id == report_id).delete()
        db.query(EvidenceItem).filter(EvidenceItem.report_id == report_id).delete()

        provider = get_ai_provider()
        
        # Preprocessing (Phase 3)
        from app.engines.preprocessing.pipeline import run_preprocessing
        
        with stage_timer(db, report.job_id, report.id, "PREPROCESSING"):
            prep_result = run_preprocessing(report.original_text)
            
            if not prep_result.is_valid:
                report.processing_status = prep_result.processing_status
                db.commit()
                audit("PROCESSING_FAILED", {"reason": prep_result.processing_status})
                return
                
            norm_record = ReportNormalization(
                report_id=report.id,
                method="deterministic",
                normalized_text=prep_result.normalized_text,
                normalization_trace=prep_result.normalization_trace,
                is_current=True,
                confidence=1.0
            )
            db.add(norm_record)
            report.normalized_text = prep_result.normalized_text

        # Phase 4: Language Gate
        from app.engines.language_gate.detector import LanguageDetector
        from app.engines.language_gate.gate import decide_routing, LanguageGateDecision
        
        with stage_timer(db, report.job_id, report.id, "LANGUAGE_GATE"):
            detector = LanguageDetector()
            detection = detector.detect(prep_result.normalized_text)
            
            report.language_code = detection.language_code
            report.language_confidence = detection.confidence
            report.is_mixed_language = detection.is_mixed
            
            decision = decide_routing(detection, len(prep_result.normalized_text))
            report.processing_path = decision.value
            
            from app.core.config import settings

        if decision == LanguageGateDecision.INSUFFICIENT_TEXT:
            report.processing_status = "INSUFFICIENT_TEXT"
            db.commit()
            audit("PROCESSING_FAILED", {"reason": "INSUFFICIENT_TEXT"})
            return
        elif decision == LanguageGateDecision.REVIEW_REQUIRED:
            report.processing_status = "REVIEW_REQUIRED"
            db.commit()
            audit("PROCESSING_FAILED", {"reason": "LANGUAGE_REVIEW_REQUIRED"})
            return
        elif decision == LanguageGateDecision.DETERMINISTIC_ENGLISH or settings.APP_MODE == "offline":
            report.ai_used = False
            if decision == LanguageGateDecision.AI_NORMALIZATION and settings.APP_MODE == "offline":
                report.processing_status = "REVIEW_REQUIRED"
                report.processing_path = "offline_no_ai"
                db.commit()
                audit("PROCESSING_SKIPPED", {"reason": "Non-English in offline mode, AI unavailable"})
                return
        else:
            # AI_NORMALIZATION
            report.ai_used = True
            try:
                with stage_timer(db, report.job_id, report.id, "AI_NORMALIZATION"):
                    max_retries = 2
                    norm_result = None
                    for attempt in range(max_retries + 1):
                        try:
                            norm_result = await provider.normalize_text(prep_result.normalized_text)
                            break
                        except Exception as e:
                            if attempt == max_retries:
                                raise e
                            logger.warning(f"AI normalization failed for {report_id}, retrying in 2s... ({e})")
                            await asyncio.sleep(2)
                    
                    db.query(ReportNormalization).filter(
                        ReportNormalization.report_id == str(report.id),
                        ReportNormalization.is_current == True
                    ).update({"is_current": False})
                    db.flush()
                    
                    ai_norm_record = ReportNormalization(
                        report_id=report.id,
                        method="ai_semantic",
                        normalized_text=norm_result.normalized_text,
                        normalization_trace=[{"rule": "ai_translation", "language": norm_result.language_detected}],
                        is_current=True,
                        confidence=norm_result.confidence
                    )
                    db.add(ai_norm_record)
                    prep_result.normalized_text = norm_result.normalized_text
                    report.normalized_text = norm_result.normalized_text
                    
                    if report.job_id:
                        from app.models.job import ProcessingJob
                        job = db.query(ProcessingJob).filter(ProcessingJob.id == report.job_id).first()
                        if job:
                            job.ai_records += 1
            except Exception as e:
                logger.error(f"Error during AI normalization for {report_id}: {e}")
                report.processing_status = "AI_NORMALIZATION_FAILED"
                report.ai_used = False
                db.commit()
                audit("PROCESSING_FAILED", {"reason": "AI_NORMALIZATION_FAILED"})
                return False

        # Phase 6 & 7: Three Brains and Decision Layer
        try:
            with stage_timer(db, report.job_id, report.id, "CORE_ENGINES"):
                sif_result, lsr_results, entity_results = await asyncio.gather(
                    sif_engine.analyze(prep_result.normalized_text, report.report_type),
                    lsr_engine.analyze(prep_result.normalized_text, report.report_type),
                    entity_engine.extract(prep_result.normalized_text)
                )

            with stage_timer(db, report.job_id, report.id, "DECISION_LAYER"):
                review_state, contradictions, updated_sif_result = decision_engine.orchestrate(sif_result, lsr_results, entity_results)
                
                if contradictions:
                    logger.warning(f"Contradictions found for report {report_id}: {contradictions}")

            with stage_timer(db, report.job_id, report.id, "SAVE_RESULTS"):
                sif_pred = SIFPrediction(
                    report_id=report.id,
                    is_current=True,
                    sif_potential=updated_sif_result["sif_potential"],
                    score=updated_sif_result["score"],
                    confidence=updated_sif_result["confidence"],
                    risk_band=updated_sif_result["risk_band"],
                    engine_name=updated_sif_result["engine"],
                    engine_version="1.0",
                    method="deterministic",
                    evidence_summary=[{"text": e["text"], "weight": e["weight"]} for e in updated_sif_result["evidence"]]
                )
                db.add(sif_pred)

                report.sif_potential = updated_sif_result["sif_potential"]
                report.sif_score = updated_sif_result["score"]
                report.risk_band = updated_sif_result["risk_band"]
                
                for e in updated_sif_result["evidence"]:
                    db.add(EvidenceItem(
                        report_id=report.id, source_type="NORMALIZED_TEXT",
                        start_offset=e.get("start", 0), end_offset=e.get("end", 0), phrase=e["text"],
                        concept=e["concept"], engine=sif_result["engine"], weight=e["weight"]
                    ))

                from app.models.life_saving_rule import LifeSavingRule
                
                for lsr_res in lsr_results:
                    rule = db.query(LifeSavingRule).filter(LifeSavingRule.rule_code == lsr_res["rule_id"]).first()
                    if rule:
                        lsr_pred = LSRPrediction(
                            report_id=report.id,
                            rule_id=rule.id,
                            is_current=True,
                            matched=True,
                            score=lsr_res["score"],
                            confidence=lsr_res["confidence"],
                            method=lsr_res["method"],
                            matched_phrases=lsr_res["matched_phrases"],
                            engine_version="1.0"
                        )
                        db.add(lsr_pred)
                        
                        for phrase_obj in lsr_res.get("matched_phrases_with_offsets", []):
                            db.add(EvidenceItem(
                                report_id=report.id, source_type="NORMALIZED_TEXT",
                                start_offset=phrase_obj.get("start", 0), end_offset=phrase_obj.get("end", 0), phrase=phrase_obj["text"],
                                concept=lsr_res["rule_id"], engine=lsr_res["method"], weight=0.8
                            ))

                from app.models.entity import Entity
                from app.models.barrier import Barrier
                
                for ent in entity_results:
                    e = Entity(
                        report_id=report.id,
                        entity_type=ent["entity_type"],
                        value=ent["value"],
                        normalized_value=ent["normalized_value"],
                        source_start=ent.get("source_start", 0),
                        source_end=ent.get("source_end", 0),
                        confidence=ent["confidence"],
                        extraction_method=ent["extraction_method"]
                    )
                    db.add(e)
                    if ent["entity_type"] == "BARRIER":
                        b = Barrier(
                            report_id=report.id,
                            barrier_name=ent["value"],
                            status=ent["status"],
                            evidence_text=ent["value"],
                            confidence=ent["confidence"]
                        )
                        db.add(b)

                try:
                    embedding = await provider.generate_embedding(report.original_text)
                    report.vector_embedding = embedding
                except Exception as e:
                    logger.error(f"Error generating embedding for {report_id}: {e}")

                if report.processing_status == "AI_NORMALIZATION_FAILED" and review_state == "COMPLETED":
                    report.processing_status = "REVIEW_RECOMMENDED"
                else:
                    report.processing_status = review_state
            
            db.commit()
            audit("PROCESSED", {"status": report.processing_status, "ai_used": report.ai_used})
            return True

        except Exception as e:
            logger.error(f"Error during deterministic analysis for {report_id}: {e}")
            db.rollback()
            report.processing_status = "REVIEW_REQUIRED"
            db.commit()
            audit("PROCESSING_FAILED", {"error": str(e)})
            return False

    except Exception as e:
        logger.error(f"Unhandled error processing report {report_id}: {e}")
        db.rollback()
        report = db.query(Report).filter(Report.id == report_id).first()
        if report:
            report.processing_status = "FAILED"
            db.commit()
            audit("PROCESSING_FAILED", {"error": str(e)})
        return False
    finally:
        db.close()

def process_report(report_id: str):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                pool.submit(lambda: asyncio.run(process_report_async(report_id))).result()
        else:
            asyncio.run(process_report_async(report_id))
    except RuntimeError:
        asyncio.run(process_report_async(report_id))

async def process_pending_reports_async():
    db: Session = SessionLocal()
    english_ids = []
    non_english_ids = []
    try:
        pending_reports = db.query(Report).filter(Report.processing_status == "READY").all()
        if not pending_reports:
            return
            
        from app.engines.language_gate.detector import LanguageDetector
        from app.engines.language_gate.gate import decide_routing, LanguageGateDecision
        detector = LanguageDetector()
        
        for r in pending_reports:
            detection = detector.detect(r.original_text)
            decision = decide_routing(detection, len(r.original_text))
            
            if decision == LanguageGateDecision.AI_NORMALIZATION:
                non_english_ids.append(str(r.id))
            else:
                english_ids.append(str(r.id))
    finally:
        db.close()

    # Process English records concurrently (fast, local execution)
    if english_ids:
        # Reduce concurrency to 5 to prevent SQLAlchemy QueuePool exhaustion
        sem = asyncio.Semaphore(5)
        async def process_with_sem(rid):
            async with sem:
                await process_report_async(rid)
        
        await asyncio.gather(*(process_with_sem(rid) for rid in english_ids))

    # Process Non-English records in batches with a circuit breaker
    if non_english_ids:
        batch_size = 5
        continuous_failures = 0
        breaker_tripped = False
        
        for i in range(0, len(non_english_ids), batch_size):
            if breaker_tripped:
                break
                
            batch = non_english_ids[i:i+batch_size]
            results = await asyncio.gather(*(process_report_async(rid) for rid in batch), return_exceptions=True)
            
            failed_in_this_batch_ids = []
            
            # Check results to update circuit breaker sequentially
            for rid, res in zip(batch, results):
                if isinstance(res, Exception) or res is False:
                    continuous_failures += 1
                    failed_in_this_batch_ids.append(rid)
                    if continuous_failures >= 3:
                        breaker_tripped = True
                else:
                    continuous_failures = 0
            
            # Send all failed reports in this batch to DLQ
            if failed_in_this_batch_ids:
                db_fail: Session = SessionLocal()
                try:
                    db_fail.query(Report).filter(Report.id.in_(failed_in_this_batch_ids)).update({"processing_status": "DLQ"}, synchronize_session=False)
                    db_fail.commit()
                except Exception as e:
                    db_fail.rollback()
                    logger.error(f"Failed to move failed batch reports to DLQ: {e}")
                finally:
                    db_fail.close()
                    
            if breaker_tripped:
                logger.error("CIRCUIT BREAKER TRIPPED: 3 continuous AI failures.")
                break
                
        if breaker_tripped:
            remaining_ids = non_english_ids[i:]
            if remaining_ids:
                db_err: Session = SessionLocal()
                try:
                    db_err.query(Report).filter(Report.id.in_(remaining_ids), Report.processing_status == "READY").update({"processing_status": "DLQ"}, synchronize_session=False)
                    db_err.commit()
                    logger.info(f"Moved {len(remaining_ids)} reports to DLQ due to tripped circuit breaker.")
                except Exception as e:
                    db_err.rollback()
                    logger.error(f"Failed to update DLQ reports: {e}")
                finally:
                    db_err.close()

def process_pending_reports():
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                pool.submit(lambda: asyncio.run(process_pending_reports_async())).result()
        else:
            asyncio.run(process_pending_reports_async())
    except RuntimeError:
        asyncio.run(process_pending_reports_async())
