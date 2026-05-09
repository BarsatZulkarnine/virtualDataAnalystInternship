"""
Tests for TICKET-003 — Patient Count Drops After Merge
======================================================
File under test : analytics_pipeline.py → merge_datasets()

The merge silently drops ~30% of patients who have NULL Insurance_ID.
Fix: change how='inner' to how='left' and join on Patient_ID only.
Fix location: analytics_pipeline.py → merge_datasets()

These tests require generated data — run patient_data_gen.py first.
"""

import sqlite3
import pandas as pd
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from analytics_pipeline import merge_datasets
from config import PATIENTS_CSV, VISITS_DB


@pytest.fixture
def loaded_data():
    if not PATIENTS_CSV.exists() or not VISITS_DB.exists():
        pytest.skip("Run patient_data_gen.py first to generate data files.")
    patients = pd.read_csv(PATIENTS_CSV)
    conn     = sqlite3.connect(VISITS_DB)
    visits   = pd.read_sql("SELECT * FROM visits", conn)
    conn.close()
    return patients, visits


def test_no_patients_lost_after_merge(loaded_data):
    """Every patient in the source CSV must appear in the merged dataset."""
    patients, visits = loaded_data
    merged = merge_datasets(patients, visits)

    unique_source = patients["Patient_ID"].nunique()
    unique_merged = merged["Patient_ID"].nunique()

    assert unique_merged == unique_source, (
        f"{unique_source - unique_merged} patient(s) were lost during the merge.\n"
        f"Source: {unique_source} unique IDs  →  Merged: {unique_merged} unique IDs.\n"
        f"Cause: the join is dropping patients who have NULL Insurance_ID.\n"
        f"Fix: change how='inner' to how='left' in merge_datasets(), "
        f"and join only on 'Patient_ID', not Insurance_ID."
    )


def test_uninsured_patients_present_after_merge(loaded_data):
    """Patients without Insurance_ID must not be excluded from the output."""
    patients, visits = loaded_data

    uninsured_ids = patients[patients["Insurance_ID"].isna()]["Patient_ID"].unique()
    if len(uninsured_ids) == 0:
        pytest.skip("No uninsured patients in this generated dataset.")

    merged = merge_datasets(patients, visits)

    missing = [pid for pid in uninsured_ids if pid not in merged["Patient_ID"].values]
    assert len(missing) == 0, (
        f"{len(missing)} uninsured patient(s) are missing from the merged dataset.\n"
        f"Example missing IDs: {missing[:3]}\n"
        f"Uninsured patients must appear in the output with NaN in visit columns."
    )


def test_merge_does_not_duplicate_patients(loaded_data):
    """
    A left join on Patient_ID can inflate row count if a patient has multiple visits.
    This test is informational — it documents expected behaviour, not a bug.
    All source Patient_IDs should be present; duplication of rows is acceptable.
    """
    patients, visits = loaded_data
    merged = merge_datasets(patients, visits)

    unique_source = patients["Patient_ID"].nunique()
    unique_merged = merged["Patient_ID"].nunique()

    assert unique_merged >= unique_source, (
        "Merged dataset has fewer unique Patient_IDs than the source — patients were lost."
    )


def test_merge_preserves_all_patient_columns(loaded_data):
    """All columns from patients.csv must be present in the merged output."""
    patients, visits = loaded_data
    merged = merge_datasets(patients, visits)

    for col in patients.columns:
        assert col in merged.columns, (
            f"Column '{col}' from patients.csv is missing in the merged dataset."
        )
