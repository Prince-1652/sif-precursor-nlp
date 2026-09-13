import asyncio
import httpx

async def f():
    async with httpx.AsyncClient() as client:
        # Get a report ID
        r = await client.get('http://localhost:8000/api/v1/reports?limit=1')
        reports = r.json()
        if not reports:
            print("No reports")
            return
        report_id = reports[0]["id"]
        
        # Clear the db first
        from app.core.config import settings
        from sqlalchemy import create_engine, text
        engine = create_engine(str(settings.DATABASE_URL))
        conn = engine.connect()
        conn.execute(text(f"UPDATE reports SET ai_summary = NULL, ai_solution = NULL WHERE id = '{report_id}'"))
        conn.commit()
        
        # Make parallel requests
        r1, r2 = await asyncio.gather(
            client.post(f'http://localhost:8000/api/v1/reports/{report_id}/second-opinion'),
            client.post(f'http://localhost:8000/api/v1/reports/{report_id}/solution')
        )
        print("Summary Status:", r1.status_code)
        print("Summary text:", r1.text)
        print("Solution Status:", r2.status_code)
        print("Solution text:", r2.text)

asyncio.run(f())
