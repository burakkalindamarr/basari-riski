"""Exploratory group-error audit on the 80% development split only.

Run:
    python experiments/audit_groups.py

Outputs: group_audit_results.csv (not independent validation)
"""
from __future__ import annotations

import pandas as pd
from sklearn.metrics import brier_score_loss, confusion_matrix, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split

from src.risk_model import build_pipeline, prepare_data

raw = pd.read_csv("data_3.csv", sep=";", encoding="utf-8-sig")
X, y = prepare_data(raw)
X_train, _, y_train, _ = train_test_split(
    X, y, stratify=y, test_size=0.2, random_state=42
)
prob = cross_val_predict(
    build_pipeline("gradient_boosting"),
    X_train, y_train,
    cv=StratifiedKFold(5, shuffle=True, random_state=42),
    method="predict_proba",
)[:, 1]

rows: list[dict] = []
for group in ("Gender", "Scholarship holder", "Displaced"):
    for code in sorted(X_train[group].unique()):
        mask = (X_train[group] == code).to_numpy()
        actual = y_train.to_numpy()[mask]
        scores = prob[mask]
        predicted = (scores >= 0.50).astype(int)
        tn, fp, fn, tp = confusion_matrix(actual, predicted, labels=[0, 1]).ravel()
        rows.append({
            "group": group, "value": int(code), "n": len(actual),
            "true_failure_rate": round(float(actual.mean()), 3),
            "flagged_rate": round(float(predicted.mean()), 3),
            "recall": round(tp / (tp + fn), 3),
            "false_positive_rate": round(fp / (fp + tn), 3),
            "precision": round(tp / (tp + fp), 3) if tp + fp else None,
            "brier": round(brier_score_loss(actual, scores), 3),
            "roc_auc": round(roc_auc_score(actual, scores), 3),
        })

results = pd.DataFrame(rows)
print(results.to_string(index=False))
results.to_csv("group_audit_results.csv", index=False)
print("\nDevelopment-only audit. These metrics do not prove fairness or unfairness.")
