import os
import sys
import logging

logging.basicConfig(level=logging.DEBUG)

from app.models.base import SessionLocal
from app.services.ingestion import process_csv_upload
from app.services.processing import process_pending_reports

def run_test():
    db = SessionLocal()
    try:
        csv_path = r"F:\Projects\SIF\generated_reports_100.csv"
        with open(csv_path, 'rb') as f:
            content = f.read()
        
        print("Starting upload...")
        job = process_csv_upload(db, content, "generated_reports_100.csv")
        print(f"Job created: {job.id}, Processed: {job.processed_records}, Failed: {job.failed_records}, Status: {job.status}")
        
        print("Starting processing...")
        process_pending_reports()
        print("Processing finished.")
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    run_test()
