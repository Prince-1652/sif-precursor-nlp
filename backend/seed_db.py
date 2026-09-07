import asyncio
import os
import sys

from sqlalchemy.orm import Session
from app.models.base import SessionLocal
from app.models.report import Report
from app.models.site import Site
from app.services.ingestion import process_csv_upload
from app.services.processing import process_pending_reports

def seed_db():
    db = SessionLocal()
    try:
        print("Checking mock sites...")
        # Create some mock sites
        existing_site = db.query(Site).filter(Site.site_code == "ALPHA-01").first()
        if not existing_site:
            print("Creating mock sites...")
            sites = [
                Site(name="Alpha Facility", site_code="ALPHA-01", region="North America"),
                Site(name="Beta Plant", site_code="BETA-02", region="Europe"),
                Site(name="Gamma Platform", site_code="GAMMA-03", region="Offshore")
            ]
            db.add_all(sites)
            db.commit()
        else:
            print("Mock sites already exist.")

        # Try to load synthetic data
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(base_dir, "synthetic_reports.csv")
        
        if os.path.exists(csv_path):
            print(f"Loading synthetic reports from {csv_path}...")
            with open(csv_path, 'rb') as f:
                content = f.read()
            
            job = process_csv_upload(db, content, "synthetic_reports.csv")
            print(f"Ingested CSV as Job {job.id}")
            
            print("Processing pending reports...")
            process_pending_reports()
            
            print("Seeding complete!")
        else:
            print("synthetic_reports.csv not found. Skipped seeding reports.")

    except Exception as e:
        print(f"Seeding failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
