import os
import sys
from sqlalchemy import create_engine, text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

def clear_database():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        print("Dropping schema public...")
        conn.execute(text("DROP SCHEMA public CASCADE;"))
        print("Creating schema public...")
        conn.execute(text("CREATE SCHEMA public;"))
        conn.execute(text("GRANT ALL ON SCHEMA public TO postgres;"))
        conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    print("Database cleared successfully.")

if __name__ == "__main__":
    clear_database()
