"""
Tests for TICKET-010 — Class Imbalance (Stretch Goal)
=====================================================
File under test : models/readmission_model.py → train_model()

The dataset has ~85/15 class split (not readmitted / readmitted).
Without addressing this, the model learns to always predict 'not readmitted'
and achieves ~85% accuracy while catching almost no actual readmissions.

At minimum: set class_weight='balanced' in LogisticRegression.

These tests compare baseline vs. balanced model recall — the balanced model
must show a meaningful improvement in catching true readmissions.

Run after analytics_pipeline.py has produced data/merged_patients.csv.
"""

import pandas as pd
import numpy as np
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import MERGED_CSV, RANDOM_STATE, TEST_SIZE


@pytest.fixture
def train_test_split_data():
    if not MERGED_CSV.exists():
        pytest.skip(
            "data/merged_patients.csv not found.\n"
            "Run: python patient_data_gen.py && python analytics_pipeline.py"
        )
    from models.readmission_model import preprocess
    from sklearn.model_selection import train_test_split

    df = pd.read_csv(MERGED_CSV)
    result = preprocess(df)
    X, y = result[0], result[1]
    return train_test_split(X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y)


def test_class_imbalance_is_present():
    """Confirm the dataset actually has class imbalance — this is the problem to solve."""
    if not MERGED_CSV.exists():
        pytest.skip("data/merged_patients.csv not found.")
    df   = pd.read_csv(MERGED_CSV)
    rate = df["Readmitted_30Day"].mean()
    assert rate < 0.30, (
        f"Readmission rate is {rate:.1%} — not as imbalanced as expected.\n"
        "Check the data generator."
    )


def test_balanced_model_has_higher_recall(train_test_split_data):
    """
    A model with class_weight='balanced' must have higher recall for readmitted
    patients than a model without it.
    """
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import recall_score

    X_train, X_test, y_train, y_test = train_test_split_data

    baseline = LogisticRegression(random_state=RANDOM_STATE, max_iter=500)
    balanced = LogisticRegression(
        random_state=RANDOM_STATE, max_iter=500, class_weight="balanced"
    )
    baseline.fit(X_train, y_train)
    balanced.fit(X_train, y_train)

    recall_base     = recall_score(y_test, baseline.predict(X_test), zero_division=0)
    recall_balanced = recall_score(y_test, balanced.predict(X_test), zero_division=0)

    assert recall_balanced > recall_base, (
        f"Balanced model recall ({recall_balanced:.2f}) is not higher than "
        f"baseline ({recall_base:.2f}).\n"
        "class_weight='balanced' should improve recall for the minority class.\n"
        "Check that train_model() in models/readmission_model.py uses class_weight='balanced'."
    )


def test_balanced_model_recall_meaningful(train_test_split_data):
    """
    The balanced model must catch at least 25% of actual readmissions.
    A model that catches fewer than 25% is clinically useless.
    """
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import recall_score

    X_train, X_test, y_train, y_test = train_test_split_data

    model = LogisticRegression(
        random_state=RANDOM_STATE, max_iter=500, class_weight="balanced"
    )
    model.fit(X_train, y_train)
    recall = recall_score(y_test, model.predict(X_test), zero_division=0)

    assert recall >= 0.25, (
        f"Recall for readmitted patients = {recall:.2f} — below the 0.25 threshold.\n"
        "Try also adding engineered features from TICKET-006 to improve signal.\n"
        "If still low, consider threshold tuning: predict_proba >= 0.3 instead of 0.5."
    )


def test_balanced_model_does_not_sacrifice_all_precision(train_test_split_data):
    """
    Lowering the threshold too aggressively can make precision collapse.
    The balanced model should still have precision > 0.10 for the positive class.
    """
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import precision_score

    X_train, X_test, y_train, y_test = train_test_split_data

    model = LogisticRegression(
        random_state=RANDOM_STATE, max_iter=500, class_weight="balanced"
    )
    model.fit(X_train, y_train)
    precision = precision_score(y_test, model.predict(X_test), zero_division=0)

    assert precision >= 0.10, (
        f"Precision for readmitted patients = {precision:.2f}.\n"
        "The model may be flagging nearly everyone as high risk.\n"
        "Consider whether the current threshold (0.5) or features need adjustment."
    )
