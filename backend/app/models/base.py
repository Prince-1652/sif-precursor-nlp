from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Import all models here for Alembic to detect them automatically
from app.models.site import Site
from app.models.report import Report
from app.models.job import ProcessingJob, ProcessingAttempt
from app.models.audit import AuditEvent
