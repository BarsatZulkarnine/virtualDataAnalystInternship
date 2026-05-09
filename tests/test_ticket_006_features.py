"""
Tests for TICKET-006 — Feature Engineering
===========================================
Expected output : four new columns in data/merged_patients.csv
  Length_of_Stay  — integer days (Discharge_Date - Admission_Date)
  Age_Group       — categorical: '18-40', '41-60', '61-80', '80+'
  Has_Insurance   — binary int: 1 if insured, 0 if not
  High_BP         — binary int: 1 if Blood_Pressure >= 140, 0 otherwise

Prerequisite: TICKET-001 must be fixed first (date parsing).
Run after analytics_pipeline.py with the feature engineering applied.
"""

import pandas as pd
import numpy as np
import pytest
import sys
from pathlib import Path

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


# ── Length_of_Stay ────────────────────────────────────────────────────────────

def test_length_of_stay_column_exists(merged_df):
    assert "Length_of_Stay" in merged_df.columns, (
        "Column 'Length_of_Stay' not found in merged_patients.csv.\n"
        "Add: df['Length_of_Stay'] = (Discharge_Date - Admission_Date).dt.days\n"
        "Requires TICKET-001 to be done first."
    )


def test_length_of_stay_non_negative(merged_df):
    if "Length_of_Stay" not in merged_df.columns:
        pytest.skip("Length_of_Stay column not present.")
    negative = (merged_df["Length_of_Stay"] < 0).sum()
    assert negative == 0, (
        f"{negative} rows have a negative Length_of_Stay.\n"
        "Discharge_Date - Admission_Date should always be >= 0."
    )


def test_length_of_stay_plausible_range(merged_df):
    if "Length_of_Stay" not in merged_df.columns:
        pytest.skip("Length_of_Stay column not present.")
    assert merged_df["Length_of_Stay"].max() <= 365, (
        "Some Length_of_Stay values exceed 365 days — likely a date parsing issue."
    )


# ── Age_Group ─────────────────────────────────────────────────────────────────

def test_age_group_column_exists(merged_df):
    assert "Age_Group" in merged_df.columns, (
        "Column 'Age_Group' not found in merged_patients.csv.\n"
        "Add: df['Age_Group'] = pd.cut(df['Age'], bins=[17,40,60,80,120], "
        "labels=['18-40','41-60','61-80','80+'])"
    )


def test_age_group_has_exactly_four_categories(merged_df):
    if "Age_Group" not in merged_df.columns:
        pytest.skip("Age_Group column not present.")
    valid = {"18-40", "41-60", "61-80", "80+"}
    actual = set(merged_df["Age_Group"].dropna().astype(str).unique())
    unexpected = actual - valid
    assert not unexpected, (
        f"Unexpected Age_Group values: {unexpected}.\n"
        f"Only these four categories are allowed: {valid}"
    )


def test_age_group_no_nulls(merged_df):
    if "Age_Group" not in merged_df.columns:
        pytest.skip("Age_Group column not present.")
    nulls = merged_df["Age_Group"].isna().sum()
    assert nulls == 0, (
        f"{nulls} rows have a null Age_Group.\n"
        "All patients have a known Age — Age_Group should have no nulls."
    )


# ── Has_Insurance ─────────────────────────────────────────────────────────────

def test_has_insurance_column_exists(merged_df):
    assert "Has_Insurance" in merged_df.columns, (
        "Column 'Has_Insurance' not found.\n"
        "Add: df['Has_Insurance'] = df['Insurance_ID'].notna().astype(int)"
    )


def test_has_insurance_is_binary(merged_df):
    if "Has_Insurance" not in merged_df.columns:
        pytest.skip("Has_Insurance column not present.")
    values = set(merged_df["Has_Insurance"].dropna().unique())
    assert values <= {0, 1}, (
        f"Has_Insurance should contain only 0 and 1, found: {values}"
    )


def test_has_insurance_matches_insurance_id(merged_df):
    if "Has_Insurance" not in merged_df.columns:
        pytest.skip("Has_Insurance column not present.")
    mismatch = (
        merged_df["Insurance_ID"].notna().astype(int) != merged_df["Has_Insurance"]
    ).sum()
    assert mismatch == 0, (
        f"{mismatch} rows have Has_Insurance that doesn't match Insurance_ID nullability."
    )


# ── High_BP ───────────────────────────────────────────────────────────────────

def test_high_bp_column_exists(merged_df):
    assert "High_BP" in merged_df.columns, (
        "Column 'High_BP' not found.\n"
        "Add: df['High_BP'] = (df['Blood_Pressure'] >= 140).astype(int)"
    )


def test_high_bp_is_binary(merged_df):
    if "High_BP" not in merged_df.columns:
        pytest.skip("High_BP column not present.")
    values = set(merged_df["High_BP"].dropna().unique())
    assert values <= {0, 1}, (
        f"High_BP should contain only 0 and 1, found: {values}"
    )


def test_high_bp_matches_blood_pressure(merged_df):
    if "High_BP" not in merged_df.columns:
        pytest.skip("High_BP column not present.")
    known = merged_df.dropna(subset=["Blood_Pressure", "High_BP"])
    expected = (known["Blood_Pressure"] >= 140).astype(int)
    mismatch = (expected != known["High_BP"]).sum()
    assert mismatch == 0, (
        f"{mismatch} rows have High_BP that doesn't match Blood_Pressure >= 140."
    )
