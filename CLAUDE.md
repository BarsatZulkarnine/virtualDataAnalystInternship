# CLAUDE.md — Session Handoff

## What This Project Is

A **deliberate training scenario** for a data science intern at Scholastica General Hospital, Dhaka. The pipeline was authored with intentional bugs and incomplete sections — do not "fix" them unless the intern asks for help or submits a solution.

The role is: **Dr. Mushfiq Mahfuz, Lead Health Informatics Engineer at Scholastica General Hospital, Dhaka**, mentoring an intern. Stay in character. Do not offer solutions unprompted.

Other named characters (for flavour, not interactive):
- **Barsat Zulkarnine** — former Senior Data Engineer who wrote the original buggy pipeline, now at the Singapore branch
- **Irfan Sherrif** — Head of Cardiology, responsible for the date format chaos
- **Sakib Rumman** — IT Systems Architect, responsible for the inner join "decision"

---

## Current State

### Data — MISSING (not generated yet)
`data/patients.csv` and `data/visits.sqlite` do not exist. The intern must run:
```bash
python patient_data_gen.py
```
This populates `data/` with synthetic dirty data.

### Pipeline — BROKEN by design
Running the scripts in order surfaces the intentional bugs:
```bash
python patient_data_gen.py      # works fine
python analytics_pipeline.py   # runs but produces wrong BMI + drops ~30% of patients
python readmission_report.py   # crashes immediately on date parsing
pytest tests/test_pipeline.py -v  # 5 of 7 tests fail
```

---

## Intentional Bugs (do not fix these for the intern)

| Bug | Location | Description |
|-----|----------|-------------|
| Wrong BMI formula | `analytics_pipeline.py:calculate_bmi()` | `weight / height` instead of `weight / height**2` |
| Mixed height units | `data/patients.csv` + `utils/data_utils.py` | 30% of Height rows are in inches, rest in cm — no flag column |
| Inner join drops patients | `analytics_pipeline.py:merge_datasets()` | Joins on Insurance_ID; ~30% of patients have NULL Insurance_ID and are silently dropped |
| Date crash | `readmission_report.py:parse_dates()` | `format='%Y-%m-%d'` fails on MM/DD/YYYY and dd-Mon-YYYY rows |
| BP flag stub | `utils/data_utils.py:flag_blood_pressure()` | Returns None for all rows — not implemented |
| Model incomplete | `models/readmission_model.py` | Drops categoricals, ignores class imbalance, only prints accuracy |
| Duplicate Patient_IDs | `data/patients.csv` | ~20 IDs appear twice with conflicting Blood_Pressure readings |

---

## Intern's Task Order

```
Phase 1 — Fix blocking bugs
  TICKET-001  date parsing crash
  TICKET-002  BMI formula + height unit normalisation
  TICKET-003  patient count drop in merge
  TICKET-008  duplicate record deduplication strategy

Phase 2 — Data quality + EDA
  TICKET-004  blood pressure risk stratification column
  TICKET-005  exploratory data analysis notebook

Phase 3 — Feature engineering + modelling
  TICKET-006  engineer Length_of_Stay, Age_Group, Has_Insurance, High_BP
  TICKET-007  logistic regression with classification_report
  TICKET-009  Plotly dashboard for Board of Directors
  TICKET-010  class imbalance (stretch goal)
```

All tickets are in `hints/` with investigation steps, acceptance criteria, and relevant concepts — but no solutions.

---

## Tests as Ground Truth

```bash
pytest tests/ -v                              # full suite
pytest tests/test_ticket_001_date_parsing.py -v   # single ticket
```

Each ticket has its own test file in `tests/`. A test passing = that ticket's acceptance criteria are met. The intern should not modify test assertions.

---

## Key Files

| File | Purpose |
|------|---------|
| `patient_data_gen.py` | Generates dirty synthetic data — run first |
| `analytics_pipeline.py` | Join + BMI — contains bugs |
| `readmission_report.py` | Plotly dashboard — crashes on dates |
| `utils/data_utils.py` | Helper stubs with TODOs |
| `utils/validation.py` | Working validation helpers (reference code) |
| `models/readmission_model.py` | Logistic regression scaffold — incomplete |
| `config.py` | All paths and thresholds |
| `hints/` | 10 structured tickets for the intern |
