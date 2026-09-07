import sys
import os
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend directory to path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.models.life_saving_rule import LifeSavingRule

# Canonical Life-Saving Rules
LSR_DATA = [
    {
        "rule_code": "BYPASSING_SAFETY_CONTROLS",
        "name": "Bypassing Safety Controls",
        "description": "Obtain authorization before overriding or disabling safety controls."
    },
    {
        "rule_code": "CONFINED_SPACE",
        "name": "Confined Space",
        "description": "Obtain authorization before entering a confined space."
    },
    {
        "rule_code": "DRIVING",
        "name": "Driving",
        "description": "Follow safe driving rules."
    },
    {
        "rule_code": "ENERGY_ISOLATION",
        "name": "Energy Isolation",
        "description": "Verify isolation and zero energy before work begins."
    },
    {
        "rule_code": "HOT_WORK",
        "name": "Hot Work",
        "description": "Control flammables and ignition sources."
    },
    {
        "rule_code": "LINE_OF_FIRE",
        "name": "Line of Fire",
        "description": "Keep yourself and others out of the line of fire."
    },
    {
        "rule_code": "SAFE_MECHANICAL_LIFTING",
        "name": "Safe Mechanical Lifting",
        "description": "Plan lifting operations and control the area."
    },
    {
        "rule_code": "WORKING_AT_HEIGHT",
        "name": "Working at Height",
        "description": "Protect yourself against a fall when working at height."
    },
    {
        "rule_code": "PERMIT_TO_WORK",
        "name": "Permit to Work",
        "description": "Work with a valid permit when required."
    }
]

def seed():
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        count = 0
        for rule_data in LSR_DATA:
            existing = db.query(LifeSavingRule).filter(LifeSavingRule.rule_code == rule_data["rule_code"]).first()
            if not existing:
                new_rule = LifeSavingRule(**rule_data)
                db.add(new_rule)
                count += 1
        
        if count > 0:
            db.commit()
            print(f"Successfully seeded {count} Life-Saving Rules.")
        else:
            print("Life-Saving Rules already seeded. No action taken.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Seeding Life-Saving Rules...")
    seed()
