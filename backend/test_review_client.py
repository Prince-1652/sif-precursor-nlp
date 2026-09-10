from fastapi.testclient import TestClient
from app.main import app
import urllib.request, json

reports = json.loads(urllib.request.urlopen('http://localhost:8000/api/v1/reports').read().decode())
r_id = reports[0]['id']

client = TestClient(app)
try:
    response = client.post(f"/api/v1/reports/{r_id}/review", json={"decision": "CONFIRM"})
    print("STATUS CODE:", response.status_code)
    print("RESPONSE BODY:", response.json())
except Exception as e:
    import traceback
    traceback.print_exc()
