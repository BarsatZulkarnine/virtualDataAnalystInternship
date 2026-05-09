"""
Tests for TICKET-009 — Readmission Rate Visualization Dashboard
================================================================
File under test : readmission_report.py

The primary deliverable is a set of HTML files — there is no automated test
for chart content. These smoke tests verify:
  - The report script runs to completion
  - The expected HTML output files are produced

Prerequisites: TICKET-001 (date parsing), TICKET-004 (Risk_Flag column).
Run after analytics_pipeline.py has produced data/merged_patients.csv.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import MERGED_CSV, REPORTS_DIR


@pytest.fixture(autouse=True)
def require_merged_data():
    if not MERGED_CSV.exists():
        pytest.skip(
            "data/merged_patients.csv not found.\n"
            "Run: python patient_data_gen.py && python analytics_pipeline.py"
        )


def test_department_chart_is_generated():
    """
    After running readmission_report.py, the department chart HTML must exist.
    This is the primary Board deliverable.
    """
    chart = REPORTS_DIR / "readmission_by_department.html"
    assert chart.exists(), (
        f"Report not found: {chart}\n"
        "Run: python readmission_report.py\n"
        "If the script crashes, fix TICKET-001 (date parsing) first."
    )


def test_department_chart_is_valid_html():
    """The generated file must be a non-empty HTML file."""
    chart = REPORTS_DIR / "readmission_by_department.html"
    if not chart.exists():
        pytest.skip("Department chart not generated yet.")

    content = chart.read_text(encoding="utf-8")
    assert len(content) > 500, "HTML file looks empty or truncated."
    assert "<html" in content.lower() or "<!doctype" in content.lower() or "plotly" in content.lower(), (
        "Generated file does not look like valid HTML."
    )


def test_risk_tier_chart_is_generated():
    """
    Chart 2 (readmission by Risk_Flag) is required once TICKET-004 is complete.
    """
    chart = REPORTS_DIR / "readmission_by_risk_tier.html"
    assert chart.exists(), (
        f"Risk tier chart not found: {chart}\n"
        "This chart is required for TICKET-009.\n"
        "Make sure TICKET-004 (flag_blood_pressure) is done first so "
        "Risk_Flag exists in the merged dataset."
    )


def test_age_group_chart_is_generated():
    """Chart 3 (readmission by Age_Group) is required once TICKET-006 is complete."""
    chart = REPORTS_DIR / "readmission_by_age_group.html"
    assert chart.exists(), (
        f"Age group chart not found: {chart}\n"
        "This chart is required for TICKET-009.\n"
        "Make sure TICKET-006 (feature engineering) is done first so "
        "Age_Group exists in the merged dataset."
    )
