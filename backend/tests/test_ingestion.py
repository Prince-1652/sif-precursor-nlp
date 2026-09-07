def test_upload_valid_csv(client):
    csv_content = b"source_record_id,report_type,original_text\n123,UA,Some dangerous thing\n456,UC,Another danger"
    
    response = client.post(
        "/api/v1/reports/upload",
        files={"file": ("test.csv", csv_content, "text/csv")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert data["total_records"] == 2
    assert data["processed_records"] == 2
    assert data["failed_records"] == 0

def test_upload_invalid_file_extension(client):
    content = b"some text"
    
    response = client.post(
        "/api/v1/reports/upload",
        files={"file": ("test.txt", content, "text/plain")}
    )
    
    assert response.status_code == 400
    assert "Only CSV files" in response.json()["detail"]

def test_upload_csv_with_missing_text(client):
    # original_text is missing in the second row
    csv_content = b"source_record_id,report_type,original_text\n123,UA,Some danger\n456,UC,\n"
    
    response = client.post(
        "/api/v1/reports/upload",
        files={"file": ("test2.csv", csv_content, "text/csv")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "PARTIAL"
    assert data["total_records"] == 2
    assert data["processed_records"] == 1
    assert data["failed_records"] == 1

def test_duplicate_source_id(client):
    csv_content = b"source_record_id,report_type,original_text\n999,UA,Some danger\n"
    
    # First upload
    response1 = client.post(
        "/api/v1/reports/upload",
        files={"file": ("test3.csv", csv_content, "text/csv")}
    )
    assert response1.status_code == 200
    assert response1.json()["processed_records"] == 1
    
    # Second upload with same source_record_id
    response2 = client.post(
        "/api/v1/reports/upload",
        files={"file": ("test4.csv", csv_content, "text/csv")}
    )
    assert response2.status_code == 200
    # The record should fail to insert due to IntegrityError on unique constraint
    assert response2.json()["failed_records"] == 1
    assert response2.json()["processed_records"] == 0
