from app.models.base import SessionLocal
from app.models.report import Report
from datetime import datetime, timedelta, timezone

def backdate():
    db = SessionLocal()
    reports = db.query(Report).all()
    now = datetime.now(timezone.utc)
    past_date = now - timedelta(days=45)
    
    count = 0
    # Update some specific barriers so we definitely get rising/falling/stable
    # Let's say: 
    # Spill + ENERGY_ISOLATION + lockout/tagout (2 total): put 1 in past, 1 in present -> STABLE
    # Spill + ENERGY_ISOLATION + safety guard (2 total): put 2 in past, 0 in present -> FALLING
    # Unsafe Condition + ENERGY_ISOLATION + lockout/tagout (2 total): put 0 in past, 2 in present -> RISING
    # The others: just put in past or leave alone.
    
    from app.models.barrier import Barrier
    from app.models.lsr_prediction import LSRPrediction
    
    for r in reports:
        # Check what barriers this report has
        barriers = db.query(Barrier).filter(Barrier.report_id == r.id, Barrier.status == "FAILED").all()
        if barriers:
            b_names = [b.barrier_name for b in barriers]
            if "safety guard" in b_names and r.report_type == "Spill":
                # put all of these in past -> FALLING
                r.created_at = past_date
                count += 1
            elif "lockout/tagout" in b_names and r.report_type == "Spill":
                # put half in past -> STABLE
                if count % 2 == 0:
                    r.created_at = past_date
                count += 1
            elif "lockout/tagout" in b_names and r.report_type == "Unsafe Condition":
                # put all in present -> RISING
                pass
            else:
                # randomly put others in past
                if count % 2 == 1:
                    r.created_at = past_date
                count += 1
        else:
            # no barriers, just distribute randomly
            if count % 2 == 0:
                r.created_at = past_date
            count += 1

    db.commit()
    print(f"Backdated {count} reports to 45 days ago.")

if __name__ == "__main__":
    backdate()
