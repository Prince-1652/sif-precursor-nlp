import requests

url = "http://127.0.0.1:8000/api/v1/reports/upload"
file_path = "../sample_reports.csv"

with open(file_path, "rb") as f:
    files = {"file": ("sample_reports.csv", f, "text/csv")}
    response = requests.post(url, files=files)
    
print("Upload status:", response.status_code)
print(response.json())
