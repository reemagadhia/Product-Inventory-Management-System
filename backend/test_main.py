import io
import pandas as pd
from fastapi.testclient import TestClient
from main import app
from datetime import date

client = TestClient(app)


def create_excel_file(data: dict) -> bytes:
    df = pd.DataFrame(data)
    stream = io.BytesIO()
    df.to_excel(stream, index=False)
    return stream.getvalue()


def test_upload_valid_excel():
    data = {
        "Product SKU": ["SKU4"],
        "Product Name": ["Widget A"],
        "Category": ["Category 1"],
        "Purchase Date":date.today(),
        "Unit Price": [100.0],
        "Quantity": [10],
    }
    excel_bytes = create_excel_file(data)

    response = client.post(
        "/products/upload-excel",
        files={"file": ("Product-Data-1.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert response.status_code == 200
    assert "Uploaded" in response.json()["message"]

    products_resp = client.get("/products")
    assert products_resp.status_code == 200
    result = products_resp.json()


def test_upload_invalid_filetype():
    response = client.post(
        "/products/upload-excel",
        files={"file": ("Product-Data-1.txt", b"not an excel", "text/plain")},
    )
    assert response.status_code == 400
    assert "Only .xlsx or .xls files" in response.json()["detail"]


def test_upload_missing_columns():
    data = {
        "Product SKU": ["SKU1"],
        "Product Name": ["Widget A"],
        "Category": ["Category 1"],
        "Purchase Date": ["2025-01-01"],
        "Unit Price": [100.0],
    }
    excel_bytes = create_excel_file(data)

    response = client.post(
        "/products/upload-excel",
        files={"file": ("Product-Data-1.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )

    assert response.status_code == 400
    assert "Missing columns" in response.json()["detail"]


def test_upload_duplicate_rows():
    data = {
        "Product SKU": ["SKU1", "SKU1"],
        "Product Name": ["Widget A", "Widget A"],
        "Category": ["Category 1", "Category 1"],
        "Purchase Date": ["2025-01-01", "2025-01-01"],
        "Unit Price": [100.0, 100.0],
        "Quantity": [10, 20],
    }
    excel_bytes = create_excel_file(data)

    response = client.post(
        "/products/upload-excel",
        files={"file": ("Product-Data-1.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "Duplicate rows found" in detail["error"]
    assert len(detail["duplicates"]) > 0
