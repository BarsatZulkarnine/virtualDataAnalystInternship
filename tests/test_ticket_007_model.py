"""
Tests for TICKET-007 — Logistic Regression with Full Evaluation
================================================================
File under test : models/readmission_model.py → preprocess(), evaluate_model()

Two things to fix:
  1. preprocess() drops categoricals — it should one-hot encode Department + Gender
  2. evaluate_model() only prints accuracy — add classification_report

Run after analytics_pipeline.py has produced data/merged_patients.csv.
"""

import pandas as pd
import numpy as np
import pytest
import sys
from pathlib import Path
from io import StringIO
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import MERGED_CSV


@pytest.fixture
def merged_df():
    if not MERGED_CSV.exists():
        pytest.skip(
            "data/merged_patients.csv not found.\n"
            "Run: python patient_data_gen.py && python analytics_pipeline.py"
        )
    return pd.read_csv(MERGED_CSV)


def test_preprocess_returns_correct_shapes(merged_df):
    """preprocess() must return X and y with matching row counts."""
    from models.readmission_model import preprocess
    X, y, _ = preprocess(merged_df)[:3]

    assert X.shape[0] == len(y), (
        f"X has {X.shape[0]} rows but y has {len(y)} — they must match."
    )
    assert X.shape[1] >= 4, (
        f"Feature matrix has only {X.shape[1]} columns.\n"
        "After fixing TICKET-007, it should include encoded Department + Gender columns."
    )


def test_preprocess_encodes_department(merged_df):
    """
    After the fix, the feature matrix should be wider than the 4 raw numeric columns.
    Department alone has 5 categories — one-hot encoding adds ~4 dummy columns.
    """
    from models.readmission_model import preprocess
    result = preprocess(merged_df)
    X = result[0]

    n_departments = merged_df["Department"].nunique()
    assert X.shape[1] > 4, (
        f"Feature matrix has {X.shape[1]} columns — likely still dropping categoricals.\n"
        f"One-hot encoding Department ({n_departments} categories) + Gender should "
        f"produce at least {4 + n_departments - 1} feature columns.\n"
        f"Fix: use pd.get_dummies(df, columns=['Department', 'Gender'], drop_first=True)"
    )


def test_evaluate_model_prints_recall(merged_df, capsys):
    """evaluate_model() output must include precision/recall/F1, not just accuracy."""
    from models.readmission_model import preprocess, train_model, evaluate_model
    from sklearn.model_selection import train_test_split
    from config import RANDOM_STATE, TEST_SIZE

    result  = preprocess(merged_df)
    X, y    = result[0], result[1]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    model = train_model(X_train, y_train)
    evaluate_model(model, X_test, y_test)

    captured = capsys.readouterr().out
    assert "recall" in captured.lower() or "f1" in captured.lower(), (
        "evaluate_model() output does not contain 'recall' or 'f1'.\n"
        "Add sklearn.metrics.classification_report to evaluate_model().\n"
        "Accuracy alone is misleading on an 85/15 class split."
    )


def test_model_recall_above_random_baseline(merged_df):
    """
    The model's recall for the positive class must beat the random baseline (~0.15).
    A model that always predicts 'not readmitted' gets recall = 0 for class 1.
    """
    from models.readmission_model import preprocess, train_model
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import recall_score
    from config import RANDOM_STATE, TEST_SIZE

    result  = preprocess(merged_df)
    X, y    = result[0], result[1]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    model  = train_model(X_train, y_train)
    y_pred = model.predict(X_test)
    recall = recall_score(y_test, y_pred, zero_division=0)

    assert recall > 0.10, (
        f"Recall for readmitted patients = {recall:.2f} — barely above zero.\n"
        "The model is predicting 'not readmitted' for almost everyone.\n"
        "Fixes to try:\n"
        "  1. Add one-hot encoded categoricals (TICKET-007)\n"
        "  2. Add engineered features from TICKET-006\n"
        "  3. Use class_weight='balanced' in LogisticRegression (TICKET-010)"
    )
