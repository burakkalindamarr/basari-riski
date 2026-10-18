import io
from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

from backend.main import app, load_model

ROOT = Path(__file__).resolve().parents[2]
client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["model"] == "loaded"


def test_demo_uses_real_model():
    response = client.get("/api/demo")
    assert response.status_code == 200
    result = response.json()
    assert result["source"] == "demo"
    assert result["summary"]["count"] == 849
    assert result["summary"]["low"] + result["summary"]["medium"] + result["summary"]["high"] == 849
    assert result["features"] == 16
    assert result["algorithm"] == "GradientBoostingClassifier"
    assert len(result["students"]) == 849
    assert all(0 <= s["risk"] <= 100 for s in result["students"])


def test_upload_valid():
    original = pd.read_csv(ROOT / "ornek_ogrenciler.csv").head(3)
    content = original.to_csv(index=False).encode("utf-8-sig")
    response = client.post("/api/analyze", files={
        "file": ("students.csv", content, "text/csv")
    })
    assert response.status_code == 200, response.text
    assert response.json()["summary"]["count"] == 3
    assert response.json()["source"] == "upload"


def test_upload_missing_column():
    original = pd.read_csv(ROOT / "ornek_ogrenciler.csv").head(2)
    original = original.drop(columns=["Admission grade"])
    response = client.post("/api/analyze", files={
        "file": ("students.csv", original.to_csv(index=False), "text/csv")
    })
    assert response.status_code == 422
    assert "Admission grade" in response.json()["detail"]


def test_upload_wrong_file_type():
    response = client.post("/api/analyze", files={"file": ("x.txt", b"abc", "text/plain")})
    assert response.status_code == 415


def test_upload_duplicate_ids_and_formula_rejection():
    original = pd.read_csv(ROOT / "ornek_ogrenciler.csv").head(2)
    original.loc[:, "ogrenci_no"] = ["100", "100"]
    response = client.post("/api/analyze", files={"file": ("students.csv", original.to_csv(index=False), "text/csv")})
    assert response.status_code == 422
    original.loc[:, "ogrenci_no"] = ["=1+1", "102"]
    response = client.post("/api/analyze", files={"file": ("students.csv", original.to_csv(index=False), "text/csv")})
    assert response.status_code == 422


def test_upload_missing_or_invalid_numeric_value():
    original = pd.read_csv(ROOT / "ornek_ogrenciler.csv").head(2)
    original.loc[original.index[0], "Admission grade"] = float("nan")
    response = client.post("/api/analyze", files={"file": ("students.csv", original.to_csv(index=False), "text/csv")})
    assert response.status_code == 422


def test_reject_oversized_upload():
    response = client.post("/api/analyze", files={
        "file": ("students.csv", b"a" * (2 * 1024 * 1024 + 1), "text/csv")
    })
    assert response.status_code == 413


def test_shap_matches_binary_probability():
    import numpy as np
    from scipy.special import expit

    response = client.get("/api/demo")
    assert response.status_code == 200, response.text
    item = response.json()["students"][0]
    explanation = item["explanation"]
    assert explanation["unit"] == "log_odds"
    assert abs(float(expit(explanation["predicted_log_odds"])) - item["risk"] / 100) < .001
    labels = [feature["feature"] for feature in explanation["increases"] + explanation["decreases"]]
    assert len(labels) == len(set(labels))
    assert all(isinstance(f["contribution"], float) for f in explanation["increases"])


def test_schema_contains_16_features_and_real_options():
    response = client.get("/api/schema")
    assert response.status_code == 200, response.text
    fields = response.json()["fields"]
    assert len(fields) == 16
    assert len(set(f["name"] for f in fields)) == 16
    course = next(f for f in fields if f["name"] == "Course")
    assert len(course["options"]) > 5
    assert any("Hemşirelik" in choice["label"] for choice in course["options"])


def test_manual_input_matches_demo_prediction():
    schema_response = client.get("/api/schema")
    assert schema_response.status_code == 200, schema_response.text
    sample = {field["name"]: field["default"] for field in schema_response.json()["fields"]}
    response = client.post("/api/predict", json={"id": "TEST-001", "student": sample})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["summary"]["count"] == 1
    assert result["source"] == "manual"
    assert result["students"][0]["id"] == "TEST-001"
    assert result["students"][0]["explanation"]["unit"] == "log_odds"


def test_manual_rejects_invalid_code():
    schema = client.get("/api/schema").json()
    sample = {field["name"]: field["default"] for field in schema["fields"]}
    sample["Course"] = 123456789
    response = client.post("/api/predict", json={"id": "TEST-002", "student": sample})
    assert response.status_code == 422


def test_manual_rejects_unexpected_features():
    schema = client.get("/api/schema").json()
    sample = {field["name"]: field["default"] for field in schema["fields"]}
    sample["Target"] = 1
    response = client.post("/api/predict", json={"id": "TEST-003", "student": sample})
    assert response.status_code == 422


def test_upload_rejects_leaky_or_unnecessary_columns():
    original = pd.read_csv(ROOT / "ornek_ogrenciler.csv").head(2)
    original["Target"] = "Graduate"
    response = client.post("/api/analyze", files={
        "file": ("students.csv", original.to_csv(index=False), "text/csv")
    })
    assert response.status_code == 422
    assert "Target" in response.json()["detail"]


def test_upload_rejects_unknown_category():
    original = pd.read_csv(ROOT / "ornek_ogrenciler.csv").head(2)
    original.loc[original.index[0], "Course"] = 123456789
    response = client.post("/api/analyze", files={
        "file": ("students.csv", original.to_csv(index=False), "text/csv")
    })
    assert response.status_code == 422


def test_api_response_disables_browser_caching():
    response = client.get("/api/demo")
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-content-type-options"] == "nosniff"
