"""
Tests for TICKET-008 — Duplicate Patient Record Deduplication
=============================================================
Files under test : utils/validation.py  → check_for_duplicates()  (already works)
                   utils/data_utils.py  → deduplicate_patients()   (stub — needs fix)

The check_for_duplicates() tests should PASS immediately.
The deduplicate_patients() tests FAIL until the strategy is implemented.

Fix location: utils/data_utils.py → deduplicate_patients()
"""

import pandas as pd
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.validation import check_for_duplicates
from utils.data_utils import deduplicate_patients


# ── Fixture ───────────────────────────────────────────────────────────────────

@pytest.fixture
def patients_with_duplicates():
    """Four patients; SGH-00001 and SGH-00002 each appear twice with differing BP."""
    return pd.DataFrame({
        "Patient_ID":     ["SGH-00001", "SGH-00002", "SGH-00001", "SGH-00003", "SGH-00002"],
        "Blood_Pressure": [130,          120,          155,          90,           100],
        "Admission_Date": ["2023-01-01", "2023-02-01", "2023-03-01", "2023-04-01", "2023-05-01"],
        "Age":            [45,           60,            45,           72,            60],
    })


# ── check_for_duplicates() — already correct, should PASS ────────────────────

def test_duplicate_detection_finds_correct_count(patients_with_duplicates):
    """check_for_duplicates() must count 4 duplicate rows (2 IDs × 2 rows each)."""
    result = check_for_duplicates(patients_with_duplicates, "Patient_ID")
    assert result["duplicate_rows"] == 4, (
        f"Expected 4 duplicate rows, got {result['duplicate_rows']}."
    )


def test_duplicate_detection_finds_correct_affected_ids(patients_with_duplicates):
    """Two distinct Patient_IDs are affected."""
    result = check_for_duplicates(patients_with_duplicates, "Patient_ID")
    assert result["unique_affected_ids"] == 2, (
        f"Expected 2 affected IDs, got {result['unique_affected_ids']}."
    )


def test_duplicate_detection_lists_affected_ids(patients_with_duplicates):
    """example_ids should include both affected Patient_IDs."""
    result = check_for_duplicates(patients_with_duplicates, "Patient_ID")
    assert "SGH-00001" in result["example_ids"]
    assert "SGH-00002" in result["example_ids"]


def test_no_duplicates_returns_zero(patients_with_duplicates):
    """A clean DataFrame should report zero duplicates."""
    clean = patients_with_duplicates.drop_duplicates(subset="Patient_ID")
    result = check_for_duplicates(clean, "Patient_ID")
    assert result["duplicate_rows"] == 0


# ── deduplicate_patients() — fails until implemented ─────────────────────────

def test_deduplication_removes_all_duplicate_ids(patients_with_duplicates):
    """After deduplication every Patient_ID must appear exactly once."""
    result = deduplicate_patients(patients_with_duplicates, key="Patient_ID")

    dup_count = result.duplicated("Patient_ID").sum()
    assert dup_count == 0, (
        f"{dup_count} duplicate Patient_IDs remain after deduplicate_patients().\n"
        "The function must reduce every Patient_ID to a single row."
    )


def test_deduplication_preserves_all_unique_ids(patients_with_duplicates):
    """No patient should be completely removed — only duplicates collapsed."""
    result     = deduplicate_patients(patients_with_duplicates, key="Patient_ID")
    source_ids = set(patients_with_duplicates["Patient_ID"].unique())
    result_ids = set(result["Patient_ID"].unique())

    lost = source_ids - result_ids
    assert not lost, (
        f"Patient IDs entirely missing after deduplication: {lost}\n"
        "deduplicate_patients() should reduce duplicates to one row, not delete patients."
    )


def test_deduplication_output_row_count(patients_with_duplicates):
    """5 rows (3 unique IDs + 2 duplicates) → 3 rows after deduplication."""
    result = deduplicate_patients(patients_with_duplicates, key="Patient_ID")
    assert len(result) == 3, (
        f"Expected 3 rows after deduplication, got {len(result)}.\n"
        "SGH-00001 and SGH-00002 each appear twice — both should collapse to one row."
    )


def test_deduplication_strategy_is_documented(patients_with_duplicates):
    """
    Whichever strategy is chosen, it must be deterministic — calling the function
    twice on the same input must return the same result.
    """
    result_a = deduplicate_patients(patients_with_duplicates.copy(), key="Patient_ID")
    result_b = deduplicate_patients(patients_with_duplicates.copy(), key="Patient_ID")

    ids_a = sorted(result_a["Patient_ID"].tolist())
    ids_b = sorted(result_b["Patient_ID"].tolist())
    assert ids_a == ids_b, (
        "deduplicate_patients() returned different results on two identical inputs.\n"
        "The strategy must be deterministic."
    )
