"""
Project configuration for the St. Gemini Memorial Readmission Pipeline.
Centralises all paths, thresholds, and constants — edit here, not in scripts.
"""

from pathlib import Path

BASE_DIR  = Path(__file__).parent
DATA_DIR  = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"

PATIENTS_CSV = DATA_DIR / "patients.csv"
VISITS_DB    = DATA_DIR / "visits.sqlite"
MERGED_CSV   = DATA_DIR / "merged_patients.csv"

# ── Clinical thresholds ────────────────────────────────────────────────────
BP_HIGH_THRESHOLD     = 140   # systolic mmHg → High Priority
BP_MODERATE_THRESHOLD = 90    # systolic mmHg → Moderate  (below → Monitor)

BMI_LOWER_BOUND = 10
BMI_UPPER_BOUND = 60

# ── Model parameters ───────────────────────────────────────────────────────
RANDOM_STATE = 42
TEST_SIZE    = 0.20
EXPECTED_READMISSION_RATE = 0.15   # ~15 % positive class

# ── Domain constants ───────────────────────────────────────────────────────
DEPARTMENTS = [
    "Cardiology",
    "Oncology",
    "Orthopedics",
    "Neurology",
    "General Medicine",
]
