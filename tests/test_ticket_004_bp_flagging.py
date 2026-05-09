"""
Tests for TICKET-004 — Blood Pressure Risk Stratification
==========================================================
File under test : utils/data_utils.py → flag_blood_pressure()

The function is a stub — it returns None for every row.
Fix: implement the three-tier AHA classification using np.select or pd.cut.
Fix location: utils/data_utils.py → flag_blood_pressure()

AHA tiers:
  BP >= 140        → 'High Priority'
  90 <= BP < 140   → 'Moderate'
  BP < 90          → 'Monitor'
  NaN              → NaN
"""

import pandas as pd
import numpy as np
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_utils import flag_blood_pressure


def test_function_is_implemented():
    """Fails immediately if flag_blood_pressure() is still a stub returning None."""
    result = flag_blood_pressure(pd.Series([120]))
    assert result is not None, (
        "flag_blood_pressure() returned None — the function is not yet implemented.\n"
        "See utils/data_utils.py → flag_blood_pressure() and the TODO comment."
    )


def test_returns_series_not_list():
    """Output must be a pd.Series so it can be assigned directly to a DataFrame column."""
    result = flag_blood_pressure(pd.Series([120, 160, 80]))
    assert isinstance(result, pd.Series), (
        f"Expected pd.Series, got {type(result).__name__}.\n"
        "Return pd.Series(...) not a plain list or numpy array."
    )


def test_high_priority_above_140():
    """Systolic BP >= 140 → 'High Priority'."""
    result = flag_blood_pressure(pd.Series([150, 180, 200]))
    for i, bp in enumerate([150, 180, 200]):
        assert result.iloc[i] == "High Priority", (
            f"BP={bp} → expected 'High Priority', got '{result.iloc[i]}'."
        )


def test_boundary_exactly_140_is_high_priority():
    """BP = 140 is exactly on the boundary — must be 'High Priority' (>= not >)."""
    result = flag_blood_pressure(pd.Series([140]))
    assert result.iloc[0] == "High Priority", (
        f"BP=140 → expected 'High Priority', got '{result.iloc[0]}'.\n"
        f"The condition is BP >= 140 (inclusive), not BP > 140."
    )


def test_moderate_between_90_and_139():
    """90 <= BP < 140 → 'Moderate'."""
    result = flag_blood_pressure(pd.Series([90, 120, 139]))
    for i, bp in enumerate([90, 120, 139]):
        assert result.iloc[i] == "Moderate", (
            f"BP={bp} → expected 'Moderate', got '{result.iloc[i]}'."
        )


def test_boundary_exactly_90_is_moderate():
    """BP = 90 is the lower boundary of 'Moderate' — must not be 'Monitor'."""
    result = flag_blood_pressure(pd.Series([90]))
    assert result.iloc[0] == "Moderate", (
        f"BP=90 → expected 'Moderate', got '{result.iloc[0]}'.\n"
        f"The Moderate range is 90 <= BP < 140 (90 is inclusive)."
    )


def test_monitor_below_90():
    """Systolic BP < 90 → 'Monitor' (hypotensive)."""
    result = flag_blood_pressure(pd.Series([89, 70, 60]))
    for i, bp in enumerate([89, 70, 60]):
        assert result.iloc[i] == "Monitor", (
            f"BP={bp} → expected 'Monitor', got '{result.iloc[i]}'."
        )


def test_nan_input_produces_nan_output():
    """Missing BP reading must produce NaN — not a string, not 'None', not 0."""
    result = flag_blood_pressure(pd.Series([np.nan]))
    assert pd.isna(result.iloc[0]), (
        f"NaN input → expected NaN output, got '{result.iloc[0]}'.\n"
        "Do not assign a risk tier to patients with missing blood pressure readings.\n"
        "Hint: np.select() fills the default for NaN — you need to restore NaN explicitly."
    )


def test_mixed_series_all_correct():
    """End-to-end: a realistic mix of values including a NaN."""
    bp     = pd.Series([160, 125, 82, 140, 89, np.nan])
    result = flag_blood_pressure(bp)

    expected = ["High Priority", "Moderate", "Monitor", "High Priority", "Monitor", None]
    for i, (val, exp) in enumerate(zip(result, expected)):
        if exp is None:
            assert pd.isna(val), f"Index {i}: expected NaN, got '{val}'"
        else:
            assert val == exp, f"BP={bp.iloc[i]} → expected '{exp}', got '{val}'"
