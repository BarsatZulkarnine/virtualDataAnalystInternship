"""
Data validation helpers for the St. Gemini Memorial readmission pipeline.

These functions are used by analytics_pipeline.py to surface data quality
issues without crashing the run.  They print warnings; they do not raise.
"""

import pandas as pd
from config import BMI_LOWER_BOUND, BMI_UPPER_BOUND


def check_for_duplicates(df: pd.DataFrame, key_col: str) -> dict:
    """
    Report on duplicate values in a key column.

    Parameters
    ----------
    df      : DataFrame to inspect
    key_col : name of the column that should be unique (e.g. 'Patient_ID')

    Returns
    -------
    dict with keys:
        duplicate_rows       — total number of rows involved in a duplication
        unique_affected_ids  — number of distinct IDs that appear more than once
        example_ids          — up to 5 example affected IDs
    """
    dup_mask = df.duplicated(subset=key_col, keep=False)
    dup_count = int(dup_mask.sum())
    affected  = df.loc[dup_mask, key_col].unique()

    if dup_count > 0:
        print(
            f"[WARN] {dup_count} rows share a non-unique '{key_col}' "
            f"({len(affected)} distinct IDs affected).  "
            f"Examples: {affected[:5].tolist()}"
        )
    else:
        print(f"[OK]  No duplicate '{key_col}' values found.")

    return {
        "duplicate_rows":      dup_count,
        "unique_affected_ids": int(len(affected)),
        "example_ids":         affected[:5].tolist(),
    }


def validate_bmi_range(df: pd.DataFrame, bmi_col: str = "BMI") -> None:
    """
    Warn if any BMI values fall outside the plausible human range.

    A healthy adult BMI sits between roughly 10 and 60.  Values outside
    this range strongly suggest a formula or unit error upstream.
    """
    if bmi_col not in df.columns:
        print(f"[WARN] Column '{bmi_col}' not present — BMI validation skipped.")
        return

    out_of_range = df[
        (df[bmi_col] < BMI_LOWER_BOUND) | (df[bmi_col] > BMI_UPPER_BOUND)
    ]
    pct = len(out_of_range) / max(len(df), 1) * 100

    if len(out_of_range) > 0:
        print(
            f"[WARN] {len(out_of_range)} rows ({pct:.1f}%) have BMI outside "
            f"[{BMI_LOWER_BOUND}, {BMI_UPPER_BOUND}].  "
            f"Observed range: {df[bmi_col].min():.1f} – {df[bmi_col].max():.1f}. "
            f"Possible unit or formula error — see TICKET-002."
        )
    else:
        print(
            f"[OK]  All BMI values within expected range "
            f"[{BMI_LOWER_BOUND}, {BMI_UPPER_BOUND}]."
        )


def validate_no_nulls(df: pd.DataFrame, required_cols: list) -> None:
    """
    Verify that required columns contain no null values.

    Prints one line per column.
    """
    for col in required_cols:
        if col not in df.columns:
            print(f"[WARN] Required column '{col}' is missing from DataFrame.")
            continue
        null_count = int(df[col].isna().sum())
        if null_count > 0:
            print(f"[WARN] '{col}' has {null_count} null value(s).")
        else:
            print(f"[OK]  '{col}' — no nulls.")
