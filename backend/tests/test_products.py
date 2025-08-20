import io
import pandas as pd
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def create_excel_file(data: dict) -> bytes:
    """Helper: create in-memory Excel file from dict."""
    df = pd.DataFrame(data)
    stream = io.BytesIO()
    df.to_excel(stream, index=False)
    return stream.getvalue()


def test_upload_valid_excel():
    # Arrange
    data = {
        "Product SKU": ["SKU1"],
        "Product Name": ["Widget A"],
        "Category": ["Category 1"],
        "Purchase Date": ["2025-01-01"],
        "Unit Price": [100.0],
        "Quantity": [10],
    }
    excel_bytes = create_excel_file(data)

    # Act: upload
    response = client.post(
        "/upload-excel",  # ✅ your actual route name
        files={"file": ("test.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )

    # Assert upload succeeded
    assert response.status_code == 200
    assert "Uploaded" in response.json()["message"]

    # Act: fetch products
    products_resp = client.get("/products")
    assert products_resp.status_code == 200
    result = products_resp.json()

    # Assert product exists
    assert len(result) == 1
    assert result[0]["Product SKU"] == "SKU1"
    assert "Stock Age (Days)" in result[0]


def test_upload_invalid_filetype():
    response = client.post(
        "/upload-excel",
        files={"file": ("test.txt", b"not an excel", "text/plain")},
    )
    assert response.status_code == 400
    assert "Only .xlsx or .xls files" in response.json()["detail"]


def test_upload_missing_columns():
    # Missing Quantity column
    data = {
        "Product SKU": ["SKU1"],
        "Product Name": ["Widget A"],
        "Category": ["Category 1"],
        "Purchase Date": ["2025-01-01"],
        "Unit Price": [100.0],
    }
    excel_bytes = create_excel_file(data)

    response = client.post(
        "/upload-excel",
        files={"file": ("test.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
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
        "/upload-excel",
        files={"file": ("Product-Repository.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "Duplicate rows found" in detail["error"]
    assert len(detail["duplicates"]) > 0
