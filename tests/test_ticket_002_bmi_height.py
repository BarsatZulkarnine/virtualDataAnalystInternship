"""
Tests for TICKET-002 — Wrong BMI Formula + Mixed Height Units
=============================================================
Files under test : analytics_pipeline.py  → calculate_bmi()
                   utils/data_utils.py    → normalize_height()

Two compounding bugs — both must be fixed for all tests to pass.
Fix locations:
  1. analytics_pipeline.py  line ~58  (calculate_bmi — missing ** 2)
  2. utils/data_utils.py    (normalize_height — inch detection missing)
"""

import pandas as pd
import numpy as np
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from analytics_pipeline import calculate_bmi
from utils.data_utils import normalize_height
from utils.validation import validate_bmi_range


# ── calculate_bmi() ───────────────────────────────────────────────────────────

def test_bmi_known_reference_value():
    """70 kg, 1.75 m → BMI = 70 / 1.75² = 22.857."""
    result = calculate_bmi(70.0, 1.75)
    assert abs(result - 22.86) < 0.1, (
        f"Expected BMI ≈ 22.86, got {result:.4f}.\n"
        f"The formula should be weight / height**2, not weight / height.\n"
        f"Check analytics_pipeline.py → calculate_bmi()."
    )


def test_bmi_formula_uses_squared_height():
    """Confirm the exponent: dividing by height (not height²) gives ~40 for this case."""
    result_correct = calculate_bmi(70.0, 1.75)
    wrong_result   = 70.0 / 1.75   # what the buggy formula produces

    assert abs(result_correct - wrong_result) > 10, (
        "calculate_bmi() looks like it may still be using weight / height.\n"
        "The correct formula is weight / height**2."
    )


def test_bmi_plausible_for_realistic_adults():
    """BMI for any valid adult input must sit in [10, 60]."""
    cases = [
        (50,  1.55, "lightweight, short"),
        (120, 2.00, "heavy, tall"),
        (65,  1.70, "average"),
        (90,  1.80, "slightly overweight"),
    ]
    for weight, height, label in cases:
        bmi = calculate_bmi(weight, height)
        assert 10 <= bmi <= 60, (
            f"BMI {bmi:.2f} is outside [10, 60] for {label} "
            f"(weight={weight} kg, height={height} m).\n"
            f"If BMI > 60, the formula is likely missing the ** 2 exponent."
        )


# ── normalize_height() ────────────────────────────────────────────────────────

def test_normalize_height_leaves_cm_unchanged():
    """Heights already in cm (>100) should not be converted."""
    df = pd.DataFrame({"Height": [175, 160, 190]})
    result = normalize_height(df)

    assert "Height_m" in result.columns, (
        "normalize_height() must add a 'Height_m' column."
    )
    assert abs(result["Height_m"].iloc[0] - 1.75) < 0.01, (
        "175 cm should become Height_m = 1.75. "
        "CM values must not be double-converted."
    )


def test_normalize_height_converts_inches_to_cm():
    """Heights in inches (<100) must be converted to cm before dividing by 100."""
    df = pd.DataFrame({"Height": [65, 70, 72]})  # inches
    result = normalize_height(df)

    expected_m = [65 * 2.54 / 100, 70 * 2.54 / 100, 72 * 2.54 / 100]
    for i, exp in enumerate(expected_m):
        assert abs(result["Height_m"].iloc[i] - exp) < 0.01, (
            f"Height {df['Height'].iloc[i]} inches → expected Height_m ≈ {exp:.3f}, "
            f"got {result['Height_m'].iloc[i]:.3f}.\n"
            f"Hint: 1 inch = 2.54 cm. Detect inch rows with: Height < 100."
        )


def test_normalize_height_mixed_units():
    """Realistic mix: some cm rows, some inch rows in the same column."""
    df = pd.DataFrame({"Height": [170, 65, 182, 72]})   # [cm, in, cm, in]
    result = normalize_height(df)

    assert abs(result["Height_m"].iloc[0] - 1.70) < 0.01, "170 cm → 1.70 m"
    assert abs(result["Height_m"].iloc[1] - 1.651) < 0.01, "65 in → 1.651 m"
    assert abs(result["Height_m"].iloc[2] - 1.82) < 0.01, "182 cm → 1.82 m"
    assert abs(result["Height_m"].iloc[3] - 1.829) < 0.01, "72 in → 1.829 m"

    too_short = (result["Height_m"] < 1.40).any()
    assert not too_short, (
        "After normalization, no adult patient should have Height_m < 1.40 m.\n"
        "Values that small suggest inch rows were not converted before dividing by 100."
    )


# ── validate_bmi_range() (already works — should pass immediately) ────────────

def test_validate_bmi_range_warns_on_bad_values(capsys):
    """validate_bmi_range() should print [WARN] for out-of-range BMI values."""
    bad_df = pd.DataFrame({"BMI": [22.5, 850.0, 18.1, 4200.0]})
    validate_bmi_range(bad_df)
    captured = capsys.readouterr()
    assert "[WARN]" in captured.out, (
        "validate_bmi_range() should print a [WARN] line when BMI > 60."
    )


def test_validate_bmi_range_ok_on_clean_values(capsys):
    """validate_bmi_range() should print [OK] when all BMI values are plausible."""
    good_df = pd.DataFrame({"BMI": [18.5, 22.0, 30.1, 25.4]})
    validate_bmi_range(good_df)
    captured = capsys.readouterr()
    assert "[OK]" in captured.out
