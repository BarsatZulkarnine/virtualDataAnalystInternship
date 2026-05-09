"""
Scholastica General Hospital, Dhaka — Patient Data Generator
------------------------------------------------------
Generates synthetic patient records and visit logs for the 30-day readmission
analysis pipeline.

  Run this script FIRST:   python patient_data_gen.py

Outputs
-------
  data/patients.csv    — ~2,400 patient rows (contains deliberate data quality issues)
  data/visits.sqlite   — 6,000 visit records in SQLite (table: visits)
"""

import numpy as np
import pandas as pd
import sqlite3
import random
from pathlib import Path

from config import DATA_DIR, DEPARTMENTS, RANDOM_STATE

np.random.seed(RANDOM_STATE)
random.seed(RANDOM_STATE)

N_PATIENTS  = 2000
N_VISITS    = 6000

# ── Name pools (mix of Bangladeshi and international — reflects Dhaka's patient population)
_FIRST_NAMES = [
    "Rahim", "Karim", "Farhan", "Nusrat", "Tasnim", "Rafi", "Mehrab", "Zara",
    "Anika", "Saad", "Tahmid", "Lamia", "Ishmam", "Nadia", "Arif", "Sadia",
    "Rakib", "Maliha", "Jubayer", "Fahmida", "Tanvir", "Sumaiya", "Rifat", "Nafisa",
    "Imran", "Tanha", "Shadman", "Humaira", "Nilufar", "Mahir", "Afra", "Zubayer",
    "Samira", "Rezwan", "Lubna", "Tahsin", "Raisa", "Mushfiq", "Irfan", "Sakib",
    "Barsat", "Fariha", "Nahid", "Shirin", "Maruf", "Dilruba", "Ashraf", "Parisa",
]
_LAST_NAMES = [
    "Hossain", "Islam", "Rahman", "Ahmed", "Chowdhury", "Khan", "Akter", "Begum",
    "Malik", "Miah", "Sarkar", "Bhuiyan", "Siddiqui", "Noor", "Kabir", "Uddin",
    "Zaman", "Haider", "Sheikh", "Alam", "Talukder", "Mondal", "Dewan", "Huq",
    "Rashid", "Sultana", "Abedin", "Mostafa", "Choudhury", "Reza", "Zulkarnine",
    "Mahfuz", "Sherrif", "Rumman", "Faruq", "Billah", "Nawaz", "Kamal", "Basher",
]

_DIAGNOSES = [
    "Hypertensive heart disease", "Type 2 diabetes mellitus",
    "Community-acquired pneumonia", "Congestive heart failure",
    "Chronic obstructive pulmonary disease", "Sepsis",
    "Acute myocardial infarction", "Ischaemic stroke",
    "Hip fracture", "Colorectal cancer",
    "Breast cancer", "Chronic kidney disease",
    "Urinary tract infection", "Deep vein thrombosis",
    "Pulmonary embolism", "Appendicitis",
    "Gastrointestinal haemorrhage", "Cellulitis",
    "Atrial fibrillation", "Asthma exacerbation",
]

_PROCEDURE_CODES = [
    "99213", "99214", "99232", "93000", "71046",
    "80053", "85025", "36415", "93306", "70553",
    "27447", "43239", "45378", "52000",
]


def _random_name() -> str:
    return f"{random.choice(_FIRST_NAMES)} {random.choice(_LAST_NAMES)}"


def _format_date_mixed(dt: pd.Timestamp, fmt_choice: int) -> str:
    """Return a date string in one of three deliberately inconsistent formats."""
    if fmt_choice == 0:
        return dt.strftime("%Y-%m-%d")     # ISO-8601  →  2024-03-15
    elif fmt_choice == 1:
        return dt.strftime("%m/%d/%Y")     # US        →  03/15/2024
    else:
        return dt.strftime("%d-%b-%Y")     # UK/EU     →  15-Mar-2024


def generate_patients_csv(path: Path) -> None:
    patient_ids = [f"SGH-{str(i).zfill(5)}" for i in range(1, N_PATIENTS + 1)]
    names       = [_random_name() for _ in range(N_PATIENTS)]
    ages        = np.random.randint(18, 89, size=N_PATIENTS)
    genders     = np.random.choice(["M", "F"], size=N_PATIENTS)
    departments = np.random.choice(DEPARTMENTS, size=N_PATIENTS)

    # ── Intentional dirty data #1 — mixed height units (no flag column) ────
    #    70 % of rows: height in cm  (152–196)
    #    30 % of rows: height in inches (59–79)
    #    Both land in the same "Height" column — no unit indicator.
    in_inches_mask = np.random.rand(N_PATIENTS) < 0.30
    heights = np.where(
        in_inches_mask,
        np.random.randint(59, 79, size=N_PATIENTS),    # inches
        np.random.randint(152, 196, size=N_PATIENTS),  # cm
    )

    weights_kg = np.random.randint(50, 120, size=N_PATIENTS)

    # ── Insurance_ID — ~30 % NULL (uninsured / self-pay patients) ──────────
    insurance_ids = [
        f"INS-{np.random.randint(10000, 99999)}" if np.random.rand() > 0.30 else None
        for _ in range(N_PATIENTS)
    ]

    blood_pressure = np.random.randint(70, 180, size=N_PATIENTS)

    # Readmission label — realistic ~15 % positive rate
    readmitted = np.random.choice([0, 1], size=N_PATIENTS, p=[0.85, 0.15])

    # Dates
    base_date       = pd.Timestamp("2023-01-01")
    admission_dates = [
        base_date + pd.Timedelta(days=int(np.random.randint(0, 365)))
        for _ in range(N_PATIENTS)
    ]
    los_days        = np.random.randint(1, 14, size=N_PATIENTS)
    discharge_raw   = [
        admission_dates[i] + pd.Timedelta(days=int(los_days[i]))
        for i in range(N_PATIENTS)
    ]

    # ── Intentional dirty data #2 — mixed date formats ────────────────────
    fmt_choices    = np.random.choice([0, 1, 2], size=N_PATIENTS)
    discharge_strs = [_format_date_mixed(discharge_raw[i], fmt_choices[i]) for i in range(N_PATIENTS)]
    admission_strs = [d.strftime("%Y-%m-%d") for d in admission_dates]

    diagnoses = np.random.choice(_DIAGNOSES, size=N_PATIENTS)

    df = pd.DataFrame({
        "Patient_ID":       patient_ids,
        "Name":             names,
        "Age":              ages,
        "Gender":           genders,
        "Height":           heights,
        "Weight_kg":        weights_kg,
        "Department":       departments,
        "Admission_Date":   admission_strs,
        "Discharge_Date":   discharge_strs,
        "Insurance_ID":     insurance_ids,
        "Blood_Pressure":   blood_pressure,
        "Primary_Diagnosis": diagnoses,
        "Readmitted_30Day": readmitted,
    })

    # ── Intentional dirty data #3 — duplicate Patient_IDs with conflicting BP
    n_dups     = 20
    dup_idx    = np.random.choice(N_PATIENTS, size=n_dups, replace=False)
    dup_rows   = df.iloc[dup_idx].copy()
    bp_offsets = (
        np.random.randint(15, 31, size=n_dups)
        * np.random.choice([-1, 1], size=n_dups)
    )
    dup_rows["Blood_Pressure"] = np.clip(
        dup_rows["Blood_Pressure"].values + bp_offsets, 60, 200
    )

    df = (
        pd.concat([df, dup_rows], ignore_index=True)
        .sample(frac=1, random_state=RANDOM_STATE)
        .reset_index(drop=True)
    )

    df.to_csv(path, index=False)
    print(f"[✓] patients.csv  →  {path}  ({len(df)} rows, {n_dups} duplicate IDs injected)")


def generate_visits_sqlite(db_path: Path, patients_csv: Path) -> None:
    patients    = pd.read_csv(patients_csv)
    unique_pids = patients["Patient_ID"].dropna().unique().tolist()

    patient_sample = np.random.choice(unique_pids, size=N_VISITS, replace=True)

    ins_map       = (
        patients.drop_duplicates("Patient_ID")
        .set_index("Patient_ID")["Insurance_ID"]
        .to_dict()
    )
    insurance_ids = [ins_map.get(pid) for pid in patient_sample]

    visit_dates = [
        (pd.Timestamp("2023-01-01") + pd.Timedelta(days=int(np.random.randint(0, 400))))
        .strftime("%Y-%m-%d")
        for _ in range(N_VISITS)
    ]

    visits_df = pd.DataFrame({
        "Visit_ID":      [f"VIS-{str(i).zfill(6)}" for i in range(1, N_VISITS + 1)],
        "Patient_ID":    patient_sample,
        "Insurance_ID":  insurance_ids,
        "Visit_Date":    visit_dates,
        "Procedure_Code": np.random.choice(_PROCEDURE_CODES, size=N_VISITS),
        "Cost_USD":      np.round(np.random.uniform(150, 8500, size=N_VISITS), 2),
        "Provider_ID":   [f"DR-{np.random.randint(100, 999)}" for _ in range(N_VISITS)],
    })

    conn = sqlite3.connect(db_path)
    visits_df.to_sql("visits", conn, if_exists="replace", index=False)
    conn.close()
    print(f"[✓] visits.sqlite →  {db_path}  ({len(visits_df)} visit records)")


if __name__ == "__main__":
    DATA_DIR.mkdir(exist_ok=True)
    generate_patients_csv(DATA_DIR / "patients.csv")
    generate_visits_sqlite(DATA_DIR / "visits.sqlite", DATA_DIR / "patients.csv")
    print("\n[✓] Data generation complete. Proceed to analytics_pipeline.py")
