"""Train a candidate model without touching the public app's model.joblib.

Run from repository root:
    python -m experiments.train_candidate --algorithm gradient_boosting

The legacy 20% split is not evaluated. CV findings remain exploratory,
not independent test or external validation results.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.model_selection import train_test_split

from src.risk_model import FEATURES, build_pipeline, prepare_data


def run(data_path: Path, output_dir: Path, algorithm: str) -> None:
    payload = data_path.read_bytes()
    sha256 = hashlib.sha256(payload).hexdigest()
    raw = pd.read_csv(data_path, sep=";", encoding="utf-8-sig")
    X, y = prepare_data(raw)

    # Match the original split for reproducibility, but do not examine the
    # legacy 20% holdout: past project iterations already used those labels.
    X_train, X_old_test, y_train, _y_old_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=42
    )
    pipeline = build_pipeline(algorithm)
    pipeline.fit(X_train, y_train)

    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / f"candidate_{algorithm}.joblib"
    joblib.dump({"model": pipeline, "sutunlar": list(FEATURES)}, model_path)

    # Check that the serialized artifact works and produces the same values.
    sample = X_train.head(10)
    before = pipeline.predict_proba(sample)
    after = joblib.load(model_path)["model"].predict_proba(sample)
    np.testing.assert_allclose(before, after, rtol=0, atol=1e-12)

    metadata = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "algorithm": algorithm,
        "data_sha256": sha256,
        "feature_columns": list(FEATURES),
        "n_usable_students": int(len(X)),
        "n_development_students": int(len(X_train)),
        "n_previous_test_students_not_evaluated": int(len(X_old_test)),
        "failure_rate_in_development": float(y_train.mean()),
        "python_sklearn_version": sklearn.__version__,
        "evaluation_status": "candidate only, no fresh independent test",
        "warning": "Do not present previous test results as independent model validation.",
    }
    (output_dir / f"candidate_{algorithm}_metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Candidate saved to: {model_path}")
    print(f"Students: {len(X)} | train: {len(X_train)} | reserved (not used): {len(X_old_test)}")
    print("Serialized model reload and inference: PASS")
    print("This script intentionally does not report an independent test score.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data_3.csv"))
    parser.add_argument("--output", type=Path, default=Path("local_artifacts"))
    parser.add_argument(
        "--algorithm", choices=["gradient_boosting", "random_forest"],
        default="gradient_boosting"
    )
    args = parser.parse_args()
    run(args.data, args.output, args.algorithm)
