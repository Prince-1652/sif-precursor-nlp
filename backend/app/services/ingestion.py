import csv
import io
import hashlib
from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.report import Report
from app.models.job import ProcessingJob

def generate_source_hash(text: str) -> str:
    return hashlib.sha256(text.strip().lower().encode('utf-8')).hexdigest()

def process_csv_upload(db: Session, file_content: bytes, filename: str) -> ProcessingJob:
    decoded_content = file_content.decode('utf-8-sig')
    csv_reader = csv.DictReader(io.StringIO(decoded_content))
    
    rows = list(csv_reader)
    total_records = len(rows)
    
    existing_job = db.query(ProcessingJob).filter(
        ProcessingJob.idempotency_key == filename,
        ProcessingJob.status.in_(["RUNNING", "COMPLETED"])
    ).first()
    
    if existing_job:
        return existing_job
    
    job = ProcessingJob(
        job_type="CSV_INGESTION",
        status="RUNNING",
        total_records=total_records,
        idempotency_key=filename
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    processed = 0
    failed = 0

    for row in rows:
        try:
            with db.begin_nested():
                original_text = row.get('original_text', '').strip()
                if not original_text:
                    raise ValueError("Missing text")
                    
                source_record_id = row.get('source_record_id', '').strip() or None
                report_type = row.get('report_type', 'unknown').strip()
                
                site_id = None
                site_code = row.get('site', '').strip()
                if site_code:
                    from app.models.site import Site
                    site = db.query(Site).filter(Site.site_code == site_code).first()
                    if site:
                        site_id = site.id
                
                reported_at = None
                date_str = row.get('reported_at', '').strip() or row.get('date', '').strip()
                if date_str:
                    from datetime import datetime
                    for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%d/%m/%Y', '%m/%d/%Y'):
                        try:
                            reported_at = datetime.strptime(date_str, fmt)
                            break
                        except ValueError:
                            continue
                
                source_hash = generate_source_hash(original_text)
                
                existing = db.query(Report).filter(
                    Report.source == "csv",
                    Report.source_hash == source_hash
                ).first()
                if existing:
                    failed += 1
                    continue
                
                report = Report(
                    source="csv",
                    source_record_id=source_record_id,
                    source_hash=source_hash,
                    site_id=site_id,
                    report_type=report_type,
                    reported_at=reported_at,
                    job_id=job.id,
                    original_text=original_text,
                    processing_status="READY",
                    pipeline_version="1.0.0"
                )
                db.add(report)
                db.flush()
                
                from app.models.audit import AuditEvent
                audit = AuditEvent(
                    report_id=report.id,
                    job_id=job.id,
                    event_type="INGESTED",
                    actor_type="SYSTEM",
                    payload={"source": "csv", "filename": filename}
                )
                db.add(audit)
            processed += 1
        except IntegrityError:
            failed += 1
        except Exception:
            failed += 1

    job.processed_records = processed
    job.failed_records = failed
    job.status = "COMPLETED" if failed == 0 else ("PARTIAL" if processed > 0 else "FAILED")
    db.commit()
    
    return job
