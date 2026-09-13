from fastapi.testclient import TestClient
from app.main import app
import traceback

client = TestClient(app)
try:
    res = client.get('/api/v1/reports?limit=1').json()
    if res:
        report_id = res[0]['id']
        r = client.post(f'/api/v1/reports/{report_id}/solution')
        print("Status:", r.status_code)
        print("Text:", r.text)
except Exception as e:
    traceback.print_exc()
