"""
Scholastica General Hospital, Dhaka — Readmission Report Generator
------------------------------------------------------------
Reads the merged patient dataset and produces an interactive readmission
rate report broken down by hospital department.

Usage
-----
    python readmission_report.py

Prerequisites
-------------
    Run analytics_pipeline.py first to produce data/merged_patients.csv

Output
------
    reports/readmission_by_department.html   (Plotly interactive chart)

!! KNOWN ISSUE (see hints/TICKET-001) !!
    This script will raise a ValueError during date parsing because
    Discharge_Date contains rows in three different string formats.
    Fix parse_dates() before anything below it will execute.
"""

import webbrowser
import pandas as pd
import plotly.express as px
from pathlib import Path

from config import MERGED_CSV, REPORTS_DIR


def load_merged_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"Records loaded : {len(df)}")
    return df


def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Convert Discharge_Date and Admission_Date using the safe multi-format parser."""
    from utils.data_utils import parse_dates_safe  # noqa: F401 (shown inline above)

    df = df.copy()
    df["Discharge_Date"] = parse_dates_safe(df["Discharge_Date"])
    df["Admission_Date"]  = parse_dates_safe(df["Admission_Date"])

    assert df["Discharge_Date"].isna().sum() == 0, "Unparseable Discharge_Date rows remain"
    assert df["Admission_Date"].isna().sum()  == 0, "Unparseable Admission_Date rows remain"

    return df


def compute_length_of_stay(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Length_of_Stay"] = (df["Discharge_Date"] - df["Admission_Date"]).dt.days
    return df


def compute_readmission_rates(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("Department")
        .agg(
            Total_Patients    = ("Patient_ID",        "nunique"),
            Readmission_Rate  = ("Readmitted_30Day",  "mean"),
            Avg_LOS_Days      = ("Length_of_Stay",    "mean"),
        )
        .reset_index()
    )
    summary["Readmission_Rate_Pct"] = (summary["Readmission_Rate"] * 100).round(1)
    summary["Avg_LOS_Days"]         = summary["Avg_LOS_Days"].round(1)
    return summary


def generate_department_chart(summary: pd.DataFrame, output_path: Path) -> None:
    fig = px.bar(
        summary,
        x="Department",
        y="Readmission_Rate_Pct",
        color="Readmission_Rate_Pct",
        color_continuous_scale="Reds",
        title="30-Day Readmission Rate by Department — Scholastica General Hospital, Dhaka",
        labels={
            "Readmission_Rate_Pct": "Readmission Rate (%)",
            "Department":           "Clinical Department",
        },
        text="Readmission_Rate_Pct",
        hover_data={"Total_Patients": True, "Avg_LOS_Days": True},
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(
        yaxis_range=[0, 35],
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=13, family="Arial"),
        title_font_size=16,
        coloraxis_showscale=False,
    )
    fig.write_html(str(output_path))
    print(f"[✓] Chart saved  → {output_path}")


def run_report() -> None:
    REPORTS_DIR.mkdir(exist_ok=True)
    df = load_merged_data(MERGED_CSV)

    # ── This call will crash — fix parse_dates() first ────────────────────
    df = parse_dates(df)

    df      = compute_length_of_stay(df)
    summary = compute_readmission_rates(df)

    print(f"\nReadmission Summary:\n{summary.to_string(index=False)}\n")

    chart_path = REPORTS_DIR / "readmission_by_department.html"
    generate_department_chart(summary, chart_path)

    print(f"\n[→] Opening report in your browser...")
    webbrowser.open(chart_path.resolve().as_uri())


if __name__ == "__main__":
    run_report()
