from fastapi.testclient import TestClient
from app.main import app
import traceback

client = TestClient(app)
try:
    res = client.get('/api/v1/reports?limit=1').json()
    if res:
        r = client.post(f'/api/v1/reports/{res[0]["id"]}/second-opinion')
        print(r.status_code)
        print(r.text)
except Exception as e:
    traceback.print_exc()
