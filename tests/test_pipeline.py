"""
Unit tests for the St. Gemini Memorial readmission pipeline.

Run with:
    pytest tests/test_pipeline.py -v

Expected status BEFORE fixes
-----------------------------
  FAIL  test_bmi_calculation_known_value      ← TICKET-002
  FAIL  test_bmi_in_plausible_range           ← TICKET-002
  FAIL  test_no_patients_lost_after_merge     ← TICKET-003
  FAIL  test_date_parsing_handles_mixed_formats ← TICKET-001
  FAIL  test_bp_flagging_returns_correct_tiers ← TICKET-004
  PASS  test_duplicate_detection              (validation helper is correct)
  PASS  test_validate_bmi_range_warns         (validation helper is correct)

Your goal: all 7 tests green.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from analytics_pipeline import calculate_bmi, merge_datasets
from utils.data_utils import flag_blood_pressure, parse_dates_safe
from utils.validation import check_for_duplicates, validate_bmi_range


# ── TICKET-002  BMI formula ────────────────────────────────────────────────

def test_bmi_calculation_known_value():
    """
    Reference case: 70 kg patient, 1.75 m tall → BMI = 70 / 1.75² ≈ 22.86.
    FAILS while calculate_bmi uses weight / height instead of weight / height².
    """
    result = calculate_bmi(70.0, 1.75)
    assert abs(result - 22.86) < 0.1, (
        f"Expected BMI ≈ 22.86, got {result:.2f}.  "
        f"Check the formula inside calculate_bmi()."
    )


def test_bmi_in_plausible_range():
    """BMI for any realistic adult input should sit between 10 and 60."""
    cases = [
        (50,  1.55),   # small / short
        (120, 2.00),   # heavy / tall
        (65,  1.70),   # average
    ]
    for weight, height in cases:
        bmi = calculate_bmi(weight, height)
        assert 10 <= bmi <= 60, (
            f"BMI {bmi:.2f} is outside [10, 60] for "
            f"weight={weight} kg, height={height} m."
        )


# ── TICKET-003  Patient count after merge ─────────────────────────────────

def test_no_patients_lost_after_merge():
    """
    The merge should preserve ALL patients, including those without Insurance_ID.
    FAILS while merge_datasets uses an inner join on Insurance_ID.
    """
    import sqlite3
    from config import PATIENTS_CSV, VISITS_DB

    if not PATIENTS_CSV.exists() or not VISITS_DB.exists():
        pytest.skip("Run patient_data_gen.py first to generate data files.")

    patients = pd.read_csv(PATIENTS_CSV)
    conn     = sqlite3.connect(VISITS_DB)
    visits   = pd.read_sql("SELECT * FROM visits", conn)
    conn.close()

    merged           = merge_datasets(patients, visits)
    unique_source    = patients["Patient_ID"].nunique()
    unique_merged    = merged["Patient_ID"].nunique()

    assert unique_merged == unique_source, (
        f"Expected {unique_source} unique patients after merge, "
        f"got {unique_merged}.  {unique_source - unique_merged} patients were lost."
    )


# ── TICKET-001  Date parsing ───────────────────────────────────────────────

def test_date_parsing_handles_mixed_formats():
    """
    parse_dates_safe() must handle ISO-8601, US (MM/DD/YYYY), and UK (dd-Mon-YYYY).
    FAILS while the implementation only accepts '%Y-%m-%d'.
    """
    mixed = pd.Series([
        "2024-03-15",    # ISO-8601
        "03/15/2024",    # US
        "15-Mar-2024",   # UK / EU
        "2023-11-01",    # ISO-8601
        "07/04/2023",    # US
        "22-Sep-2023",   # UK / EU
    ])
    result = parse_dates_safe(mixed)

    assert pd.api.types.is_datetime64_any_dtype(result), (
        "parse_dates_safe() should return a datetime64 Series."
    )
    assert result.notna().all(), (
        f"Some dates could not be parsed:\n{mixed[result.isna()].tolist()}"
    )


# ── TICKET-004  Blood pressure risk flags ─────────────────────────────────

def test_bp_flagging_returns_correct_tiers():
    """
    flag_blood_pressure() should classify systolic BP into three risk tiers.
    FAILS while the function is a stub returning None for every row.
    """
    bp      = pd.Series([160, 125, 82, 140, 89, np.nan])
    result  = flag_blood_pressure(bp)

    assert result is not None, (
        "flag_blood_pressure() returned None — function not yet implemented."
    )
    assert result[0] == "High Priority", (
        f"BP=160 → expected 'High Priority', got '{result[0]}'"
    )
    assert result[1] == "Moderate", (
        f"BP=125 → expected 'Moderate', got '{result[1]}'"
    )
    assert result[2] == "Monitor", (
        f"BP=82  → expected 'Monitor', got '{result[2]}'"
    )
    assert result[3] == "High Priority", (
        f"BP=140 → expected 'High Priority' (boundary), got '{result[3]}'"
    )
    assert pd.isna(result[5]), (
        "NaN input should produce NaN output, not a string label."
    )


# ── Validation helpers (already correct — should PASS immediately) ─────────

def test_duplicate_detection():
    """check_for_duplicates() should correctly identify conflicting records."""
    sample = pd.DataFrame({
        "Patient_ID":     ["SGM-00001", "SGM-00002", "SGM-00001", "SGM-00003"],
        "Blood_Pressure": [130, 120, 155, 90],
    })
    result = check_for_duplicates(sample, "Patient_ID")

    assert result["duplicate_rows"]      == 2
    assert result["unique_affected_ids"] == 1
    assert "SGM-00001" in result["example_ids"]


def test_validate_bmi_range_warns(capsys):
    """validate_bmi_range() should print a warning when values are out of range."""
    bad_df = pd.DataFrame({"BMI": [22.5, 850.0, 18.1, 4200.0]})
    validate_bmi_range(bad_df)
    captured = capsys.readouterr()
    assert "[WARN]" in captured.out
