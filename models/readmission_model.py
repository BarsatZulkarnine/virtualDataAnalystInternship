"""
St. Gemini Memorial Hospital — 30-Day Readmission Prediction Model
------------------------------------------------------------------
Logistic regression baseline that predicts whether a patient will be
readmitted within 30 days of discharge.

Usage
-----
    python -m models.readmission_model
    # or from analytics_pipeline after merging:
    from models.readmission_model import train_and_evaluate
    train_and_evaluate()

Incomplete sections
-------------------
  - preprocess()    : categorical columns are dropped, not encoded  → TICKET-006 / TICKET-007
  - train_model()   : class imbalance is not addressed              → TICKET-010
  - evaluate_model(): only reports accuracy                         → TICKET-007
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix

from config import MERGED_CSV, RANDOM_STATE, TEST_SIZE


def load_data(path=MERGED_CSV) -> pd.DataFrame:
    """Load the merged patient dataset produced by analytics_pipeline.py."""
    df = pd.read_csv(path)
    print(f"Dataset shape  : {df.shape}")
    print(f"\nTarget distribution (Readmitted_30Day):")
    print(df["Readmitted_30Day"].value_counts(normalize=True).round(3))
    return df


def preprocess(df: pd.DataFrame):
    """
    Prepare feature matrix (X) and target vector (y) for modelling.

    TODO (TICKET-006)
    -----------------
    Before calling this function, run feature engineering to create:
        Length_of_Stay  — (Discharge_Date - Admission_Date).dt.days
        Age_Group       — pd.cut bins: ['18-40', '41-60', '61-80', '80+']
        Has_Insurance   — 1 if Insurance_ID is not null, else 0
        High_BP         — 1 if Blood_Pressure >= 140, else 0

    TODO (TICKET-007)
    -----------------
    Categorical columns (Department, Gender) are currently dropped.
    Use pd.get_dummies() or sklearn's OneHotEncoder to encode them —
    dropping them removes clinically relevant signal.
    """
    numeric_features = ["Age", "Weight_kg", "Blood_Pressure", "BMI"]
    target_col       = "Readmitted_30Day"

    df_clean = df.dropna(subset=numeric_features + [target_col]).copy()

    X = df_clean[numeric_features]
    y = df_clean[target_col]

    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    print(f"\nFeature matrix : {X_scaled.shape}")
    print(f"Class balance  : {pd.Series(y).value_counts().to_dict()}")
    return X_scaled, y.values, scaler


def train_model(X_train: np.ndarray, y_train: np.ndarray) -> LogisticRegression:
    """
    Fit a logistic regression classifier.

    TODO (TICKET-010)
    -----------------
    class_weight is not set — the model will learn to always predict
    'not readmitted' (majority class) and still achieve ~85 % accuracy.
    Set class_weight='balanced' or explore SMOTE oversampling.
    """
    model = LogisticRegression(
        random_state=RANDOM_STATE,
        max_iter=500,
        # class_weight="balanced"   ← uncomment as part of TICKET-010
    )
    model.fit(X_train, y_train)
    return model


def evaluate_model(
    model: LogisticRegression,
    X_test: np.ndarray,
    y_test: np.ndarray,
) -> None:
    """
    Print model performance metrics.

    TODO (TICKET-007)
    -----------------
    Accuracy alone is misleading when classes are imbalanced (~85/15 split).
    Add: precision, recall, F1-score, and the confusion matrix.
    Use sklearn.metrics.classification_report for a compact summary.
    """
    y_pred = model.predict(X_test)
    acc    = accuracy_score(y_test, y_pred)
    cm     = confusion_matrix(y_test, y_pred)

    print("\n── Model Evaluation ──────────────────────────────")
    print(f"  Accuracy  : {acc:.3f}")
    print(f"  Confusion matrix:\n{cm}")
    print("  (Add precision / recall / F1 — see TICKET-007)")
    print("──────────────────────────────────────────────────")


def train_and_evaluate() -> None:
    """End-to-end training run."""
    df = load_data()
    X, y, _ = preprocess(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    model = train_model(X_train, y_train)
    evaluate_model(model, X_test, y_test)


if __name__ == "__main__":
    train_and_evaluate()
