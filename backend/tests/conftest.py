import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from app.main import app
from app.api.deps import get_db
from app.models.base import Base

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    yield engine

@pytest.fixture(scope="function")
def db(db_engine):
    session = TestingSessionLocal()
    # Clear tables before test
    session.execute(text("TRUNCATE TABLE processing_attempts, audit_events, reports, processing_jobs, sites CASCADE"))
    session.commit()
    
    yield session
    session.close()

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]
