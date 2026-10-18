"""Fast checks for reproducibility, leakage protection, and inference."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.model_selection import train_test_split

from src.risk_model import (
    APPROVED, ENROLLED, FEATURES, build_pipeline, prepare_data
)

DATA_PATH = Path(__file__).resolve().parents[1] / "data_3.csv"


def test_features_do_not_include_outcomes():
    assert len(FEATURES) == 16
    assert "Target" not in FEATURES
    assert not any("sem" in field.lower() for field in FEATURES)
    assert "Tuition fees up to date" not in FEATURES
    assert "Debtor" not in FEATURES


def test_data_counts_and_target():
    df = pd.read_csv(DATA_PATH, sep=";", encoding="utf-8-sig")
    X, y = prepare_data(df)
    assert X.shape == (4244, 16)
    assert y.value_counts().to_dict() == {1: 2516, 0: 1728}
    assert not X.isna().any().any()


def test_impossible_labels_are_rejected():
    df = pd.read_csv(DATA_PATH, sep=";", encoding="utf-8-sig").head(100)
    df.loc[df.index[0], APPROVED] = df.loc[df.index[0], ENROLLED] + 1
    with pytest.raises(ValueError, match="Geçilen ders"):
        prepare_data(df)


@pytest.mark.parametrize("algorithm", ["gradient_boosting", "random_forest"])
def test_models_fit_and_predict_probabilities(algorithm):
    df = pd.read_csv(DATA_PATH, sep=";", encoding="utf-8-sig")
    X, y = prepare_data(df)
    X_train, X_test, y_train, _ = train_test_split(
        X, y, train_size=250, stratify=y, random_state=42
    )
    fitted = build_pipeline(algorithm).fit(X_train, y_train)
    proba = fitted.predict_proba(X_test.head(10))
    assert proba.shape == (10, 2)
    assert np.isfinite(proba).all()
    assert np.all((proba >= 0) & (proba <= 1))
    np.testing.assert_allclose(proba.sum(axis=1), 1.0)
