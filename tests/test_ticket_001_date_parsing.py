"""
Tests for TICKET-001 — Date Parsing Failure
============================================
File under test : utils/data_utils.py → parse_dates_safe()
Related script  : readmission_report.py → parse_dates()

All tests here FAIL until parse_dates_safe() handles all three date formats.
Fix location: utils/data_utils.py  (look for the TODO comment in parse_dates_safe)
"""

import pandas as pd
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_utils import parse_dates_safe


def test_parses_iso_format():
    """ISO-8601 dates (2024-03-15) — the format the current stub already handles."""
    series = pd.Series(["2024-03-15", "2023-01-01", "2022-12-31"])
    result = parse_dates_safe(series)

    assert pd.api.types.is_datetime64_any_dtype(result), (
        "parse_dates_safe() must return a datetime64 Series, not strings."
    )
    assert result.notna().all(), "ISO dates should all parse without becoming NaT."


def test_parses_us_format():
    """US format (MM/DD/YYYY) — sourced from the South Wing EHR system."""
    series = pd.Series(["03/15/2024", "07/04/2023", "12/01/2022"])
    result = parse_dates_safe(series)

    assert result.notna().all(), (
        "US-format dates (MM/DD/YYYY) were not parsed.\n"
        "Hint: pd.to_datetime() with a single format= will crash on these.\n"
        "Try iterating over multiple formats or use errors='coerce'."
    )
    assert result.iloc[0] == pd.Timestamp("2024-03-15"), (
        "'03/15/2024' should parse to 2024-03-15."
    )


def test_parses_uk_hybrid_format():
    """UK/EU hybrid (dd-Mon-YYYY) — from retrospectively digitised paper records."""
    series = pd.Series(["15-Mar-2024", "22-Sep-2023", "01-Jan-2022"])
    result = parse_dates_safe(series)

    assert result.notna().all(), (
        "UK-style dates (dd-Mon-YYYY, e.g. '15-Mar-2024') were not parsed.\n"
        "Hint: the format string for this pattern is '%d-%b-%Y'."
    )
    assert result.iloc[0] == pd.Timestamp("2024-03-15"), (
        "'15-Mar-2024' should parse to 2024-03-15."
    )


def test_handles_all_three_formats_mixed():
    """All three formats in one Series — the real-world scenario from patients.csv."""
    mixed = pd.Series([
        "2024-03-15",   # ISO
        "03/15/2024",   # US
        "15-Mar-2024",  # UK
        "2023-11-01",   # ISO
        "07/04/2023",   # US
        "22-Sep-2023",  # UK
    ])
    result = parse_dates_safe(mixed)

    assert pd.api.types.is_datetime64_any_dtype(result), (
        "Return type must be datetime64."
    )
    assert result.notna().all(), (
        f"These dates failed to parse: {mixed[result.isna()].tolist()}\n"
        "parse_dates_safe() must handle all three formats in a single call."
    )


def test_unparseable_date_becomes_nat_not_exception():
    """
    A truly garbage date string should produce NaT, not crash the pipeline.
    The function must never raise ValueError on bad input.
    """
    series = pd.Series(["2024-03-15", "NOT-A-DATE", "2023-01-01"])
    try:
        result = parse_dates_safe(series)
    except Exception as e:
        pytest.fail(
            f"parse_dates_safe() raised {type(e).__name__} on an unparseable string.\n"
            f"It should return NaT for bad rows instead of crashing.\n"
            f"Hint: use errors='coerce' in pd.to_datetime()."
        )
    assert pd.isna(result.iloc[1]), (
        "'NOT-A-DATE' should produce NaT, not a string or exception."
    )


def test_preserves_existing_nat():
    """NaN / None inputs should pass through as NaT — not crash, not fill."""
    series = pd.Series(["2024-03-15", None, "2023-01-01"])
    result = parse_dates_safe(series)

    assert pd.isna(result.iloc[1]), (
        "A null input should remain NaT after parsing — do not fill missing dates."
    )
