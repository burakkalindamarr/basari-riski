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
