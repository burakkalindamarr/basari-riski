"""Nested cross-validation of semester-one academic failure risk.

The legacy 20% test split has been consulted during model development,
so it is never used for model selection or performance claims here.
This script performs nested evaluation on the remaining 80%.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    brier_score_loss,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
FEATURES = [
    "Marital status", "Application mode", "Application order", "Course",
    "Daytime/evening attendance", "Previous qualification",
    "Previous qualification (grade)", "Mother's qualification",
    "Father's qualification", "Mother's occupation", "Father's occupation",
    "Admission grade", "Displaced", "Gender", "Scholarship holder",
    "Age at enrollment",
]
CATEGORICAL = [
    "Marital status", "Application mode", "Course", "Previous qualification",
    "Mother's qualification", "Father's qualification",
    "Mother's occupation", "Father's occupation",
]
NUMERIC = [c for c in FEATURES if c not in CATEGORICAL]


def pipeline():
    preprocessing = ColumnTransformer([
        ("category", OneHotEncoder(handle_unknown="ignore", min_frequency=20), CATEGORICAL),
        ("numeric", StandardScaler(), NUMERIC),
    ])
    return Pipeline([
        ("on", preprocessing),
        ("model", LogisticRegression(max_iter=1500, random_state=42)),
    ])


def run():
    df = pd.read_csv(ROOT / "data_3.csv", sep=";", encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    df = df[df["Curricular units 1st sem (enrolled)"] > 0].copy()
    y = (df["Curricular units 1st sem (enrolled)"] >
         df["Curricular units 1st sem (approved)"]).astype(int)
    X = df[FEATURES]
    assert len(X) == 4244, f"Unexpected rows: {len(X)}"
    assert len(FEATURES) == 16
    assert not X.isna().any().any(), "Missing values must be handled first"

    X_train, _X_legacy, y_train, _y_legacy = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    search_space = [
        {"model": [LogisticRegression(max_iter=1500, random_state=42)],
         "model__C": [0.3, 1.0]},
        {"model": [RandomForestClassifier(n_estimators=120, random_state=42, n_jobs=-1)],
         "model__min_samples_leaf": [3, 6]},
        {"model": [GradientBoostingClassifier(n_estimators=100, random_state=42)],
         "model__learning_rate": [0.05, 0.1]},
    ]
    outer = StratifiedKFold(n_splits=5, shuffle=True, random_state=2026)
    inner = StratifiedKFold(n_splits=3, shuffle=True, random_state=2027)
    folds = []

    print(f"Students={len(X)}, development={len(X_train)}, historical_holdout={len(_X_legacy)}", flush=True)
    for fold, (tr, te) in enumerate(outer.split(X_train, y_train), start=1):
        X_tr, X_te = X_train.iloc[tr], X_train.iloc[te]
        y_tr, y_te = y_train.iloc[tr], y_train.iloc[te]
        search = GridSearchCV(
            pipeline(), search_space, cv=inner, scoring="roc_auc",
            refit=True, n_jobs=1, error_score="raise",
        )
        search.fit(X_tr, y_tr)
        p = search.best_estimator_.predict_proba(X_te)[:, 1]
        truth = y_te.to_numpy()
        pred = (p >= .5).astype(int)
        count = int(np.ceil(len(truth) * .2))
        top = np.argsort(-p, kind="stable")[:count]
        p20 = float(truth[top].mean())

        row = {
            "fold": fold,
            "model": type(search.best_estimator_.named_steps["model"]).__name__,
            "chosen_parameters": {
                key: str(value) if key == "model" else value
                for key, value in search.best_params_.items()
            },
            "auc": float(roc_auc_score(truth, p)),
            "brier": float(brier_score_loss(truth, p)),
            "recall_05": float(recall_score(truth, pred)),
            "precision_05": float(precision_score(truth, pred, zero_division=0)),
            "f1_05": float(f1_score(truth, pred)),
            "precision_at_20": p20,
            "recall_at_20": float(truth[top].sum() / truth.sum()),
            "lift_at_20": float(p20 / truth.mean()),
        }
        folds.append(row)
        print(f"Fold {fold}/5 | {row['model']} | AUC {row['auc']:.4f} | Precision@20 {p20:.4f}", flush=True)

    cols = [
        "auc", "brier", "recall_05", "precision_05", "f1_05",
        "precision_at_20", "recall_at_20", "lift_at_20"
    ]
    metrics = pd.DataFrame(folds)[cols]
    summary = {
        c: {"mean": float(metrics[c].mean()), "std": float(metrics[c].std(ddof=1))}
        for c in cols
    }
    payload = {
        "n_students": len(X), "n_development": len(X_train),
        "n_historical_holdout": len(_X_legacy),
        "disclaimer": "Nested CV on development split only; not an independent external evaluation.",
        "folds": folds, "summary": summary,
    }

    output = ROOT / "nested_cv_results.json"
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n=== NESTED CV SUMMARY ===", flush=True)
    for k, v in summary.items():
        print(f"{k:18s} {v['mean']:.4f} ± {v['std']:.4f}", flush=True)
    print("\n=== SELECTED MODELS ===", flush=True)
    print(pd.Series([row["model"] for row in folds]).value_counts().to_string(), flush=True)
    print(f"Results written to {output.name}", flush=True)


if __name__ == "__main__":
    run()
