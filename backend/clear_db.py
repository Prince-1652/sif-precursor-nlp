from app.db import SessionLocal
from app.models.report import Report
from app.models.job import Job

db = SessionLocal()
db.query(Job).delete()
db.query(Report).delete()
db.commit()
print("Tables cleared.")
