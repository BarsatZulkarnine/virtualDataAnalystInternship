"""
Scholastica General Hospital, Dhaka — Analytics Pipeline
--------------------------------------------------
Joins patient records (CSV) with visit data (SQLite), computes BMI,
and writes a merged dataset for downstream reporting and modelling.

Usage
-----
    python analytics_pipeline.py

Prerequisites
-------------
    Run patient_data_gen.py first to populate data/

Outputs
-------
    data/merged_patients.csv
"""

import pandas as pd
import sqlite3
from pathlib import Path

from config import PATIENTS_CSV, VISITS_DB, MERGED_CSV
from utils.validation import validate_bmi_range


def load_patients(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"Patients loaded   : {len(df):>6} rows")
    return df


def load_visits(db_path: Path) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    df   = pd.read_sql("SELECT * FROM visits", conn)
    conn.close()
    print(f"Visit records     : {len(df):>6} rows")
    return df


def calculate_bmi(weight_kg: float, height: float) -> float:
    """
    Calculate Body Mass Index.

    Parameters
    ----------
    weight_kg : float
        Patient weight in kilograms.
    height : float
        Patient height in metres.

    Returns
    -------
    float
        BMI value (kg/m²).
    """
    # BUG: denominator should be height ** 2  ← intern must find this
    return weight_kg / height



def merge_datasets(patients: pd.DataFrame, visits: pd.DataFrame) -> pd.DataFrame:
    """
    Merge patient demographics with visit billing records.

    Requires Insurance_ID to match billing system records.
    """
    print(f"\nPre-merge  patient rows : {len(patients)}")
    print(f"Pre-merge  visit   rows : {len(visits)}")

    # BUG: inner join on BOTH keys — patients with NULL Insurance_ID are silently dropped
    merged = pd.merge(
        patients,
        visits[["Patient_ID", "Insurance_ID", "Visit_Date", "Procedure_Code", "Cost_USD"]],
        on=["Patient_ID", "Insurance_ID"],
        how="inner",
    )

    print(f"Post-merge rows         : {len(merged)}")
    lost = len(patients) - merged["Patient_ID"].nunique()
    if lost > 0:
        print(f"[!] {lost} patient IDs have no match in visit records.")
    return merged


def run_pipeline() -> None:
    patients = load_patients(PATIENTS_CSV)
    visits   = load_visits(VISITS_DB)

    merged = merge_datasets(patients, visits)

    # Convert height to metres for BMI — but note: some heights are in inches, not cm
    merged["Height_m"] = merged["Height"] / 100

    merged["BMI"] = merged.apply(
        lambda row: calculate_bmi(row["Weight_kg"], row["Height_m"]),
        axis=1,
    )

    print(f"\nBMI statistics (check for impossible values):")
    print(merged["BMI"].describe().round(2))

    validate_bmi_range(merged)

    merged.to_csv(MERGED_CSV, index=False)
    print(f"\n[✓] Merged dataset saved → {MERGED_CSV}  ({len(merged)} rows)")


if __name__ == "__main__":
    run_pipeline()
