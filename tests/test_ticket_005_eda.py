"""
Tests for TICKET-005 — Exploratory Data Analysis
=================================================
There is no automated test for the content of the EDA — that is a human
deliverable (a notebook or script saved to reports/).

This file contains smoke tests that verify:
  - The merged dataset exists and is readable
  - The columns expected for EDA are all present
  - Basic statistical sanity checks on the dataset

Run after analytics_pipeline.py has produced data/merged_patients.csv.
"""

import pandas as pd
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import MERGED_CSV, REPORTS_DIR


@pytest.fixture
def merged_df():
    if not MERGED_CSV.exists():
        pytest.skip(
            "data/merged_patients.csv not found.\n"
            "Run: python patient_data_gen.py && python analytics_pipeline.py"
        )
    return pd.read_csv(MERGED_CSV)


def test_merged_csv_is_readable(merged_df):
    """Merged dataset must exist and contain rows."""
    assert len(merged_df) > 0, "merged_patients.csv is empty."


def test_required_eda_columns_present(merged_df):
    """All columns needed for the EDA analysis must be present."""
    required = [
        "Patient_ID", "Age", "Gender", "Department",
        "Blood_Pressure", "Readmitted_30Day", "Admission_Date", "Discharge_Date",
    ]
    missing = [c for c in required if c not in merged_df.columns]
    assert not missing, (
        f"Columns missing from merged_patients.csv: {missing}\n"
        "These are required for the EDA. Check analytics_pipeline.py."
    )


def test_readmission_rate_is_realistic(merged_df):
    """Overall readmission rate should be in a clinically realistic range (5–40%)."""
    rate = merged_df["Readmitted_30Day"].mean()
    assert 0.05 <= rate <= 0.40, (
        f"Readmission rate is {rate:.1%} — outside the expected 5–40% range.\n"
        "This may indicate a data generation or merge issue."
    )


def test_age_values_are_adult_range(merged_df):
    """All patients should be adults (18–110 years)."""
    assert merged_df["Age"].between(18, 110).all(), (
        f"Age column contains values outside 18–110.\n"
        f"Min: {merged_df['Age'].min()}, Max: {merged_df['Age'].max()}"
    )


def test_departments_are_known_values(merged_df):
    """Department column should only contain the five known departments."""
    from config import DEPARTMENTS
    unknown = set(merged_df["Department"].dropna()) - set(DEPARTMENTS)
    assert not unknown, (
        f"Unknown department values found: {unknown}\n"
        f"Expected only: {DEPARTMENTS}"
    )


def test_eda_output_saved_to_reports():
    """
    Reminder test: the EDA deliverable must be saved to reports/.
    This test is intentionally lenient — it checks that the reports/ directory
    exists and contains at least one output file.
    """
    REPORTS_DIR.mkdir(exist_ok=True)
    outputs = list(REPORTS_DIR.glob("eda_*"))
    assert len(outputs) > 0, (
        "No EDA output files found in reports/.\n"
        "Complete TICKET-005 and save your charts or notebook to reports/."
    )
