"""Schema, leakage-free data preparation, and consistent ML pipelines."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

FEATURES = (
    "Marital status", "Application mode", "Application order", "Course",
    "Daytime/evening attendance", "Previous qualification",
    "Previous qualification (grade)", "Mother's qualification",
    "Father's qualification", "Mother's occupation", "Father's occupation",
    "Admission grade", "Displaced", "Gender", "Scholarship holder",
    "Age at enrollment",
)
CATEGORICAL = (
    "Marital status", "Application mode", "Course", "Previous qualification",
    "Mother's qualification", "Father's qualification",
    "Mother's occupation", "Father's occupation",
)
NUMERIC = tuple(column for column in FEATURES if column not in CATEGORICAL)
ENROLLED = "Curricular units 1st sem (enrolled)"
APPROVED = "Curricular units 1st sem (approved)"


def prepare_data(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Create semester-one failure target without exposing outcome columns as features."""
    data = raw.copy()
    data.columns = data.columns.str.strip()
    required = set(FEATURES) | {ENROLLED, APPROVED}
    missing = sorted(required - set(data.columns))
    if missing:
        raise ValueError(f"Eksik sütunlar: {missing}")
    if data[list(required)].isna().any().any():
        raise ValueError("Gerekli alanlarda eksik veri var; önce temizlenmeli.")
    if not np.isfinite(data[list(required)].to_numpy(dtype=float)).all():
        raise ValueError("Sayısal alanlarda sonlu olmayan değer bulundu.")
    if (data[ENROLLED] < 0).any() or (data[APPROVED] < 0).any():
        raise ValueError("Ders sayıları negatif olamaz.")
    if (data[APPROVED] > data[ENROLLED]).any():
        raise ValueError("Geçilen ders sayısı, alınan ders sayısından fazla.")
    data = data.loc[data[ENROLLED] > 0].copy()
    if data.empty:
        raise ValueError("En az bir ders alan öğrenci bulunamadı.")
    x = data.loc[:, list(FEATURES)].copy()
    y = (data[ENROLLED] > data[APPROVED]).astype(int).rename("basarisiz")
    if y.nunique() != 2:
        raise ValueError("Eğitim verisinde her iki hedef sınıf da bulunmalı.")
    return x, y


def build_pipeline(algorithm: str = "gradient_boosting") -> Pipeline:
    """Fit category encoder and scaler within each training fold, never beforehand."""
    preprocessing = ColumnTransformer([
        ("kat", OneHotEncoder(handle_unknown="ignore", min_frequency=20), list(CATEGORICAL)),
        ("say", StandardScaler(), list(NUMERIC)),
    ])
    if algorithm == "gradient_boosting":
        estimator = GradientBoostingClassifier(random_state=42)
    elif algorithm == "random_forest":
        estimator = RandomForestClassifier(
            n_estimators=300, min_samples_leaf=3, random_state=42, n_jobs=-1
        )
    else:
        raise ValueError(f"Desteklenmeyen algoritma: {algorithm}")
    return Pipeline([("on", preprocessing), ("model", estimator)])
