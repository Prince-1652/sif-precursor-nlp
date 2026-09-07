from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.api import deps
from app.schemas.job import ProcessingJobResponse
from app.models.job import ProcessingJob

router = APIRouter()

@router.get("/{job_id}", response_model=ProcessingJobResponse)
def get_job(job_id: UUID, db: Session = Depends(deps.get_db)):
    job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
