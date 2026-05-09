# Contributing Guide — Readmission Pipeline

This document describes the expected development workflow for this repository.

---

## Running Order

Scripts must be run in sequence — each step depends on the previous:

```
patient_data_gen.py
        ↓
analytics_pipeline.py
        ↓
readmission_report.py   (or models/readmission_model.py)
```

If you modify `patient_data_gen.py`, delete `data/` and regenerate before re-running downstream scripts.

---

## Data Dictionary

### `data/patients.csv`

| Column | Type | Description |
|--------|------|-------------|
| Patient_ID | string | Hospital identifier, format `SGM-NNNNN` |
| Name | string | Patient full name |
| Age | int | Age in years at admission |
| Gender | string | `M` or `F` |
| Height | numeric | ⚠️ Mixed units — some rows cm, some inches (see TICKET-002) |
| Weight_kg | float | Body weight in kilograms |
| Department | string | Admitting department |
| Admission_Date | string | ISO-8601 `YYYY-MM-DD` |
| Discharge_Date | string | ⚠️ Mixed formats — see TICKET-001 |
| Insurance_ID | string / null | Payer identifier; ~30 % NULL for uninsured patients |
| Blood_Pressure | int | Systolic blood pressure (mmHg) |
| Primary_Diagnosis | string | ICD-10 plain-text diagnosis |
| Readmitted_30Day | int | Target label: `1` = readmitted within 30 days, `0` = not |

### `data/visits.sqlite` — table: `visits`

| Column | Type | Description |
|--------|------|-------------|
| Visit_ID | string | Unique visit identifier, format `VIS-NNNNNN` |
| Patient_ID | string | Foreign key → patients.csv |
| Insurance_ID | string / null | Billing payer ID |
| Visit_Date | string | ISO-8601 visit date |
| Procedure_Code | string | CPT procedure code |
| Cost_USD | float | Billed cost in USD |
| Provider_ID | string | Treating provider identifier |

---

## Test Suite

```bash
pytest tests/test_pipeline.py -v
```

Tests are grouped by ticket number. A test failure means the corresponding bug is not yet fixed. A test pass means the acceptance criteria for that ticket are met.

Do **not** modify test assertions to make tests pass. The tests define what correct behaviour looks like — your fixes should satisfy them, not work around them.

---

## Git Workflow

- Work on a feature branch named `fix/ticket-NNN-short-description`
- One commit per logical fix — do not bundle unrelated changes
- Commit message format: `fix(TICKET-NNN): short description of what was fixed`
- Open a pull request and include:
  - What the root cause was
  - How you identified it
  - What your fix does
  - Any clinical/domain reasoning behind design decisions (especially TICKET-008)

---

## Code Style

- Python 3.10+
- 4-space indentation, no tabs
- Type hints on public functions
- Keep functions focused: one responsibility per function
- If you introduce a new utility, add it to `utils/data_utils.py` and export it from `utils/__init__.py`
- Run the test suite before opening a PR — all 7 tests must be green

---

## Clinical Conventions

- Blood pressure values in this system are **systolic** mmHg only
- BMI formula: `weight_kg / (height_m ** 2)`  — weight in kg, height in **metres**
- Length of Stay (LOS) is measured in **calendar days** (discharge day minus admission day)
- The readmission window is **30 calendar days** from discharge date
