import asyncio
import os
import sys

from sqlalchemy.orm import Session
from app.models.base import SessionLocal
from app.models.report import Report
from app.models.site import Site
from app.models.life_saving_rule import LifeSavingRule
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

        # Seed Life-Saving Rules
        existing_rules = db.query(LifeSavingRule).count()
        if existing_rules == 0:
            print("Seeding Life-Saving Rules...")
            rules = [
                LifeSavingRule(rule_code="BYPASSING_SAFETY_CONTROLS", name="Bypassing Safety Controls", description="Do not bypass or disable safety controls"),
                LifeSavingRule(rule_code="CONFINED_SPACE", name="Confined Space", description="Obtain authorization before entering a confined space"),
                LifeSavingRule(rule_code="DRIVING", name="Driving", description="Follow safe driving rules"),
                LifeSavingRule(rule_code="ENERGY_ISOLATION", name="Energy Isolation", description="Verify isolation and zero energy before work"),
                LifeSavingRule(rule_code="HOT_WORK", name="Hot Work", description="Control flammables and ignition sources"),
                LifeSavingRule(rule_code="LINE_OF_FIRE", name="Line of Fire", description="Keep yourself and others out of the line of fire"),
                LifeSavingRule(rule_code="SAFE_MECHANICAL_LIFTING", name="Safe Mechanical Lifting", description="Plan and control lifting operations"),
                LifeSavingRule(rule_code="WORKING_AT_HEIGHT", name="Working at Height", description="Protect yourself against falls"),
                LifeSavingRule(rule_code="PERMIT_TO_WORK", name="Permit to Work", description="Work with a valid permit when required"),
            ]
            db.add_all(rules)
            db.commit()
            print(f"Seeded {len(rules)} Life-Saving Rules.")
        else:
            print(f"Life-Saving Rules already exist ({existing_rules} found).")

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
