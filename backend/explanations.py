"""SHAP explanations for the deployed binary Gradient Boosting model.

Contributions are grouped back to original input features and expressed in
**log-odds**, NOT percentage points. This is crucial for honest explanations.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import shap

FEATURE_LABELS = {
    "Marital status": "Medeni durum",
    "Application mode": "Başvuru türü",
    "Application order": "Tercih sırası",
    "Course": "Bölüm",
    "Daytime/evening attendance": "Gündüz / akşam eğitimi",
    "Previous qualification": "Önceki eğitim türü",
    "Previous qualification (grade)": "Önceki eğitim notu",
    "Mother's qualification": "Anne eğitim düzeyi",
    "Father's qualification": "Baba eğitim düzeyi",
    "Mother's occupation": "Anne mesleği",
    "Father's occupation": "Baba mesleği",
    "Admission grade": "Giriş notu",
    "Displaced": "Yerinden edilme durumu",
    "Gender": "Cinsiyet",
    "Scholarship holder": "Burs durumu",
    "Age at enrollment": "Kayıt yaşı",
}

@lru_cache(maxsize=2)
def _explainer_for(estimator):
    # Model files are authored/trusted in this repository. Never accept
    # pickle/joblib from a request.
    if estimator.__class__.__name__ != "GradientBoostingClassifier":
        raise ValueError("Current explanation pipeline supports Gradient Boosting only.")
    return shap.TreeExplainer(estimator, model_output="raw")


def _original_feature(name: str, all_names: list[str]) -> str:
    raw = name.split("__", 1)[-1]
    for original in sorted(all_names, key=len, reverse=True):
        if raw == original or raw.startswith(original + "_"):
            return original
    raise ValueError(f"Unrecognized encoded feature: {name}")


def explain_rows(model, frame, risk_probabilities: np.ndarray) -> list[dict]:
    """Compute coherent signed contributions, one explanation per row."""
    transformer = model.named_steps["on"]
    estimator = model.named_steps["model"]
    transformed = transformer.transform(frame)
    if hasattr(transformed, "toarray"):
        transformed = transformed.toarray()

    explainer = _explainer_for(estimator)
    effects = np.asarray(explainer.shap_values(transformed), dtype=float)
    if effects.ndim != 2 or effects.shape[0] != len(frame):
        raise ValueError(f"Unsupported SHAP dimensions {effects.shape}")
    encoded_names = list(transformer.get_feature_names_out())
    features = list(frame.columns)
    if effects.shape[1] != len(encoded_names):
        raise ValueError("SHAP contribution count differs from encoded feature count.")

    # Binary GB raw SHAP explains decision_function in log odds.
    base = float(np.asarray(explainer.expected_value).reshape(-1)[0])
    logits = np.asarray(estimator.decision_function(transformed), dtype=float).reshape(-1)
    summed = base + effects.sum(axis=1)
    if not np.allclose(logits, summed, rtol=1e-5, atol=1e-4):
        raise ValueError("SHAP additive consistency check failed.")

    # The probabilities must correspond to those same predictions.
    from scipy.special import expit
    if not np.allclose(expit(logits), risk_probabilities, rtol=1e-5, atol=1e-5):
        raise ValueError("SHAP explanations do not match probability outputs.")

    indices: dict[str, list[int]] = {name: [] for name in features}
    for index, name in enumerate(encoded_names):
        indices[_original_feature(name, features)].append(index)

    all_explanations = []
    for row_number in range(len(frame)):
        grouped = {
            name: float(effects[row_number, encoded_indices].sum())
            for name, encoded_indices in indices.items()
        }
        positive = sorted(
            ((name, value) for name, value in grouped.items() if value > 1e-8),
            key=lambda pair: pair[1], reverse=True,
        )[:4]
        negative = sorted(
            ((name, value) for name, value in grouped.items() if value < -1e-8),
            key=lambda pair: pair[1],
        )[:4]

        def formatted(pairs):
            return [
                {"feature": name, "label": FEATURE_LABELS[name], "contribution": round(val, 4)}
                for name, val in pairs
            ]

        all_explanations.append({
            "unit": "log_odds",
            "base_value": round(base, 4),
            "predicted_log_odds": round(float(logits[row_number]), 4),
            "increases": formatted(positive),
            "decreases": formatted(negative),
        })
    return all_explanations
