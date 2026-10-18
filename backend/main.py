"""FastAPI API: existing trained model + ephemeral demo/CSV predictions.

Research prototype. Never upload identifiable student records to a public
deployment. Requests are not written to disk by this code.
"""
from __future__ import annotations

import io
import os
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile, Request
from starlette.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.explanations import explain_rows
from backend.schema import build_schema

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "model.joblib"
DEMO_PATH = ROOT / "ornek_ogrenciler.csv"
MAX_UPLOAD_BYTES = 2 * 1024 * 1024
MAX_ROWS = 2000
LOW_THRESHOLD = 50.0
HIGH_THRESHOLD = 75.0

COURSES = {
    33: "Biyoyakıt Üretim Teknolojileri", 171: "Animasyon ve Multimedya",
    8014: "Sosyal Hizmet (Akşam)", 9003: "Ziraat Mühendisliği",
    9070: "İletişim Tasarımı", 9085: "Veteriner Hemşireliği",
    9119: "Bilişim Mühendisliği", 9130: "At Yetiştiriciliği",
    9147: "İşletme", 9238: "Sosyal Hizmet",
    9254: "Turizm", 9500: "Hemşirelik",
    9556: "Ağız ve Diş Sağlığı", 9670: "Reklamcılık ve Pazarlama",
    9773: "Gazetecilik ve İletişim", 9853: "Temel Eğitim",
    9991: "İşletme (Akşam)",
}

class Contribution(BaseModel):
    feature: str
    label: str
    contribution: float


class Explanation(BaseModel):
    unit: str
    base_value: float
    predicted_log_odds: float
    increases: list[Contribution]
    decreases: list[Contribution]


class Student(BaseModel):
    id: str
    course: str
    risk: float
    level: str
    rank: int
    explanation: Explanation


class CourseStats(BaseModel):
    course: str
    count: int
    average_risk: float


class Summary(BaseModel):
    count: int
    low: int
    medium: int
    high: int
    average_risk: float


class PredictionResult(BaseModel):
    source: str
    summary: Summary
    students: list[Student]
    courses: list[CourseStats]
    algorithm: str
    features: int
    disclaimer: str


class ManualStudent(BaseModel):
    student: dict[str, float]
    id: str = "MANUEL-001"


app = FastAPI(
    title="Akademik Risk API",
    version="0.1.0",
    description="Research-only student risk predictions from a trained Gradient Boosting pipeline.",
)

# Explicitly configured origins; never wildcard CORS with public student data.
origins = [x.strip() for x in os.getenv(
    "FRONTEND_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def privacy_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Frame-Options"] = "DENY"
    return response


@lru_cache(maxsize=1)
def load_model():
    # This is a trusted model file shipped with the repository, not a user upload.
    bundle = joblib.load(MODEL_PATH)
    pipeline = bundle["model"]
    cols = list(bundle["sutunlar"])
    if len(cols) != 16 or not hasattr(pipeline, "predict_proba"):
        raise RuntimeError("Unsupported saved model artifact")
    return pipeline, cols


def checked_features(data: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    missing = [c for c in columns if c not in data.columns]
    if missing:
        raise HTTPException(
            status_code=422,
            detail="Eksik özellik sütunları: " + ", ".join(missing),
        )
    # Prevent users from unintentionally uploading names, contact information,
    # original target labels or other unnecessary sensitive columns.
    unexpected = sorted(set(data.columns) - set(columns) - {"ogrenci_no"})
    if unexpected:
        raise HTTPException(
            status_code=422,
            detail="Gereksiz veya desteklenmeyen sütunlar: " + ", ".join(unexpected),
        )
    if not (1 <= len(data) <= MAX_ROWS):
        raise HTTPException(
            status_code=422,
            detail=f"Dosyada 1 ile {MAX_ROWS} arasında öğrenci bulunmalı.",
        )
    X = data.loc[:, columns].copy()
    for col in columns:
        try:
            X[col] = pd.to_numeric(X[col], errors="raise")
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=422,
                detail=f"'{col}' sütunundaki değerler sayısal kod veya sayı olmalı.",
            ) from None
    if X.isna().any().any() or not np.isfinite(X.to_numpy(dtype=float)).all():
        raise HTTPException(
            status_code=422,
            detail="Girdi sütunlarında boş veya geçersiz sayı var.",
        )
    schema = build_schema(COURSES)
    for field in schema["fields"]:
        col = field["name"]
        if field["kind"] == "select":
            valid_codes = {opt["value"] for opt in field["options"]}
            if not X[col].isin(valid_codes).all():
                raise HTTPException(status_code=422, detail=f"Geçersiz kategori kodu: {field['label']}")
        elif not X[col].between(field["min"], field["max"]).all():
            raise HTTPException(status_code=422, detail=f"Değer aralık dışında: {field['label']}")
    if "Age at enrollment" in X and not X["Age at enrollment"].between(15, 100).all():
        raise HTTPException(status_code=422, detail="Kayıt yaşı 15–100 aralığında olmalı.")
    for binary in ("Gender", "Displaced", "Scholarship holder", "Daytime/evening attendance"):
        if binary in X and not X[binary].isin([0, 1]).all():
            raise HTTPException(
                status_code=422,
                detail=f"'{binary}' alanı 0 veya 1 olmalı.",
            )
    return X


def ids_from(data: pd.DataFrame) -> list[str]:
    if "ogrenci_no" not in data:
        return [f"O-{i + 1:04d}" for i in range(len(data))]
    raw = data["ogrenci_no"]
    if raw.isna().any():
        raise HTTPException(status_code=422, detail="Öğrenci numaraları boş olamaz.")
    ids = [str(value).strip() for value in raw]
    if any(not x or len(x) > 64 for x in ids):
        raise HTTPException(status_code=422, detail="Geçersiz öğrenci numarası.")
    if len(set(ids)) != len(ids):
        raise HTTPException(status_code=422, detail="Tekrarlanan öğrenci numaraları var.")
    # Prevent spreadsheet formula injection in any downloaded CSV.
    if any(x.lstrip().startswith(("=", "+", "-", "@")) for x in ids):
        raise HTTPException(status_code=422, detail="Öğrenci numarası formül karakteriyle başlayamaz.")
    return ids


def analyze(data: pd.DataFrame, source: str) -> PredictionResult:
    model, columns = load_model()
    data = data.copy()
    data.columns = data.columns.str.strip()
    X = checked_features(data, columns)
    ids = ids_from(data)

    probabilities = model.predict_proba(X)[:, 1]
    explanations = explain_rows(model, X, probabilities)
    p = probabilities * 100
    if not np.isfinite(p).all():
        raise HTTPException(status_code=500, detail="Model geçerli olasılık üretmedi.")

    rows = []
    for i, probability in enumerate(p):
        risk = round(float(probability), 1)
        level = "high" if risk >= HIGH_THRESHOLD else "medium" if risk >= LOW_THRESHOLD else "low"
        try:
            key = int(X.iloc[i]["Course"])
        except (ValueError, TypeError, OverflowError):
            key = -1
        rows.append({
            "id": ids[i], "course": COURSES.get(key, f"Bölüm {key}"),
            "risk": risk, "level": level, "explanation": explanations[i],
        })
    rows.sort(key=lambda r: -r["risk"])
    students = [Student(**r, rank=i + 1) for i, r in enumerate(rows)]

    course_groups: dict[str, list[float]] = {}
    for item in students:
        course_groups.setdefault(item.course, []).append(item.risk)
    courses = sorted(
        [
            CourseStats(course=key, count=len(values), average_risk=round(float(np.mean(values)), 1))
            for key, values in course_groups.items()
        ],
        key=lambda r: -r.average_risk,
    )
    summary = Summary(
        count=len(students),
        low=sum(s.level == "low" for s in students),
        medium=sum(s.level == "medium" for s in students),
        high=sum(s.level == "high" for s in students),
        average_risk=round(float(np.mean(p)), 1),
    )
    return PredictionResult(
        source=source, summary=summary, students=students, courses=courses,
        algorithm=type(model.named_steps["model"]).__name__,
        features=len(columns),
        disclaimer=(
            "Araştırma prototipi. %50/%75 seviyeleri örnek gösterim eşikleridir, "
            "kurumsal karar sınırları değildir. Tahminler kesin karar veya nedensellik göstermez."
        ),
    )


@app.get("/api/health")
def health():
    load_model()
    return {"status": "ok", "model": "loaded"}


@app.get("/api/schema")
def form_schema():
    return build_schema(COURSES)


@app.post("/api/predict", response_model=PredictionResult)
def predict_one(payload: ManualStudent):
    if set(payload.student) != set(load_model()[1]):
        missing = sorted(set(load_model()[1]) - set(payload.student))
        unexpected = sorted(set(payload.student) - set(load_model()[1]))
        raise HTTPException(
            status_code=422,
            detail=f"Özellik alanları eşleşmiyor. Eksik: {missing}; beklenmeyen: {unexpected}",
        )
    frame = pd.DataFrame([{"ogrenci_no": payload.id, **payload.student}])
    # Strict category constraints prevent silently ignoring unknown input codes.
    schema = build_schema(COURSES)
    for field in schema["fields"]:
        if field["kind"] == "select":
            allowed = {option["value"] for option in field["options"]}
            if payload.student[field["name"]] not in allowed:
                raise HTTPException(
                    status_code=422,
                    detail=f"Geçersiz kategori kodu: {field['label']}",
                )
        else:
            value = payload.student[field["name"]]
            if not field["min"] <= value <= field["max"]:
                raise HTTPException(status_code=422, detail=f"Değer aralık dışında: {field['label']}")
    return analyze(frame, "manual")


@app.get("/api/demo", response_model=PredictionResult)
def demo():
    df = pd.read_csv(DEMO_PATH, encoding="utf-8-sig", dtype={"ogrenci_no": str})
    return analyze(df, "demo")


@app.post("/api/analyze", response_model=PredictionResult)
async def analyze_csv(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=415, detail="Lütfen CSV dosyası yükleyin.")
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    await file.close()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Dosya 2 MB sınırını aşıyor.")
    if not content.strip():
        raise HTTPException(status_code=422, detail="CSV dosyası boş.")
    try:
        # Uploaded student template uses comma-separated CSV; raw source data is
        # not an acceptable student upload because it includes outcome columns.
        df = pd.read_csv(io.BytesIO(content), encoding="utf-8-sig",
                         dtype={"ogrenci_no": str})
    except (ValueError, UnicodeError, pd.errors.ParserError, pd.errors.EmptyDataError):
        raise HTTPException(
            status_code=422,
            detail="CSV okunamadı. UTF-8 ve virgülle ayrılmış şablon kullanın.",
        ) from None
    # Run CPU-bound ML/SHAP work in the worker pool, not the event loop.
    return await run_in_threadpool(analyze, df, "upload")
