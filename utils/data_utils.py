"""
Data transformation utilities for the Scholastica General Hospital readmission pipeline.

Some functions below are stubs awaiting implementation — see the hints/ tickets
for context on what each function must do and why.
"""

import pandas as pd
import numpy as np


def normalize_height(df: pd.DataFrame, height_col: str = "Height") -> pd.DataFrame:
    """
    Convert any inch-valued rows to centimetres, then derive Height_m.

    Detection rule: adult heights in cm cluster 152–196; in inches 59–79.
    A threshold of 100 cleanly separates the two populations — no valid
    adult height in inches exceeds 96" (8 ft), and no valid height in cm
    falls below 100 cm for an adult patient.
    """
    df = df.copy()

    in_inches = df[height_col] < 100
    df[height_col] = np.where(
        in_inches,
        df[height_col] * 2.54,   # inches → cm
        df[height_col],
    )

    df["Height_m"] = df[height_col] / 100
    return df


def parse_dates_safe(series: pd.Series) -> pd.Series:
    """
    Parse a mixed-format date column into pandas Timestamps.

    Tries three formats in order, filling only still-NaT rows on each pass.
    Rows that cannot be parsed in any format become NaT with a warning.
    """
    result = pd.Series(pd.NaT, index=series.index)

    for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d-%b-%Y"]:
        unparsed = result.isna() & series.notna()
        if not unparsed.any():
            break
        result[unparsed] = pd.to_datetime(
            series[unparsed], format=fmt, errors="coerce"
        )

    n_failed = result.isna().sum() - series.isna().sum()
    if n_failed > 0:
        print(f"[WARN] {n_failed} date(s) could not be parsed — set to NaT")

    return result


def flag_blood_pressure(bp_series: pd.Series) -> pd.Series:
    """
    Classify each systolic blood pressure reading into a clinical risk tier.

    Expected output
    ---------------
    BP >= 140          →  'High Priority'
    90 <= BP < 140     →  'Moderate'
    BP < 90            →  'Monitor'
    NaN / missing      →  NaN  (preserve, do not fill)

    TODO (TICKET-004)
    -----------------
    Not yet implemented — returns a Series of None values.
    Use pd.cut() or np.select() to build the classification logic.
    Remember to handle null values explicitly.
    """
    return pd.Series([None] * len(bp_series), index=bp_series.index)


def compute_bmi(weight_kg: pd.Series, height_m: pd.Series) -> pd.Series:
    """
    Compute BMI from weight (kg) and height (metres).

    Returns a float Series.  Caller is responsible for ensuring height is
    already normalised to metres and that the inch-vs-cm issue is resolved.
    """
    return weight_kg / (height_m ** 2)


def deduplicate_patients(
    df: pd.DataFrame, key: str = "Patient_ID", strategy: str = "first"
) -> pd.DataFrame:
    """
    Reduce duplicate Patient_ID rows to a single representative record.

    TODO (TICKET-008)
    -----------------
    The current strategy ('first occurrence') is a placeholder.  Clinical
    policy has not been decided.  Options to consider:

      - 'first'   : keep earliest row by original row order
      - 'latest'  : keep most-recent record by Admission_Date
      - 'max_bp'  : keep the row with the highest Blood_Pressure reading
                    (conservative / safety-first approach)

    Document whichever strategy you choose in a comment and in your PR
    description.
    """
    return df.drop_duplicates(subset=key, keep="first")
