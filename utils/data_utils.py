"""
Data transformation utilities for the Scholastica General Hospital readmission pipeline.

Some functions below are stubs awaiting implementation — see the hints/ tickets
for context on what each function must do and why.
"""

import pandas as pd
import numpy as np


def normalize_height(df: pd.DataFrame, height_col: str = "Height") -> pd.DataFrame:
    """
    Normalise height values so that all rows are expressed in centimetres,
    then add a derived Height_m column (centimetres ÷ 100).

    Known issue
    -----------
    The patients.csv file contains a mix of heights recorded in centimetres
    (typical adult range 152–196) and inches (typical adult range 59–79).
    There is NO flag column to distinguish them.

    TODO (TICKET-002)
    -----------------
    Current implementation blindly divides every value by 100, which means
    inch-valued rows produce nonsensical Height_m values (e.g. 0.63 m for a
    65-inch patient).  Detect which rows are in inches and convert them to
    centimetres BEFORE the division.
    """
    df = df.copy()
    # Only divides — does NOT handle the inch rows
    df["Height_m"] = df[height_col] / 100
    return df


def parse_dates_safe(series: pd.Series) -> pd.Series:
    """
    Parse a date column that may contain mixed format strings into
    pandas Timestamps.

    TODO (TICKET-001)
    -----------------
    Currently hardcoded to ISO-8601 ('%Y-%m-%d').  The column also contains
    rows formatted as MM/DD/YYYY and dd-Mon-YYYY, which will raise ValueError.
    Implement a robust multi-format parser that handles all three formats and
    returns NaT (with a warning) for any rows that still cannot be parsed.
    """
    return pd.to_datetime(series, format="%Y-%m-%d")


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
