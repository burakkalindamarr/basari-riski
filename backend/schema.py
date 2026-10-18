"""Front-end input metadata derived from the dataset's original code values.

Descriptions never invent meanings for unspecified categorical codes.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.risk_model import CATEGORICAL, FEATURES
from backend.explanations import FEATURE_LABELS

ROOT = Path(__file__).resolve().parents[1]
BINARY_LABELS: dict[str, dict[int, str]] = {
    "Gender": {0: "Kadın (0)", 1: "Erkek (1)"},
    "Displaced": {0: "Hayır (0)", 1: "Evet (1)"},
    "Scholarship holder": {0: "Burs yok (0)", 1: "Burslu (1)"},
    "Daytime/evening attendance": {0: "Akşam (0)", 1: "Gündüz (1)"},
}
NUMERIC_INFO = {
    "Application order": (0, 15, 1),
    "Previous qualification (grade)": (0, 200, 1),
    "Admission grade": (0, 200, 1),
    "Age at enrollment": (15, 100, 1),
}


def build_schema(course_labels: dict[int, str]) -> dict:
    df = pd.read_csv(ROOT / "data_3.csv", sep=";", encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    # CSV demo row is an existing example, not a fabricated combination.
    demo = pd.read_csv(ROOT / "ornek_ogrenciler.csv").iloc[0]

    entries = []
    for col in FEATURES:
        is_category = col in CATEGORICAL or col in BINARY_LABELS
        default = float(demo[col])
        entry: dict = {
            "name": col,
            "label": FEATURE_LABELS[col],
            "kind": "select" if is_category else "number",
            "default": default,
        }
        if is_category:
            options = []
            for value in sorted(df[col].dropna().unique()):
                val = int(value)
                if col == "Course":
                    label = course_labels.get(val, f"Bölüm kodu {val}")
                elif col in BINARY_LABELS:
                    label = BINARY_LABELS[col].get(val, str(val))
                else:
                    label = f"Kod {val}"
                options.append({"value": val, "label": label})
            entry["options"] = options
        else:
            lo, hi, step = NUMERIC_INFO[col]
            entry.update({"min": lo, "max": hi, "step": step})
        entries.append(entry)
    return {
        "fields": entries,
        "notes": "Kategorik kodlar kaynak veri sözlüğüne bağlıdır. Kodun anlamı bilinmiyorsa yalnızca numarası gösterilir.",
        "source": "UCI academic success dataset; demonstration example",
    }
