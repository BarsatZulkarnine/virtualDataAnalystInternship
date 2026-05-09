# TICKET-006 — Feature Engineering for Readmission Risk

**Priority:** 🟠 MEDIUM — prerequisite for TICKET-007  
**Type:** Feature Engineering  
**Affects:** `analytics_pipeline.py` or a new `features.py` module  
**Test:** No automated test — verify by inspecting merged CSV output columns

---

## Problem Description

The current `models/readmission_model.py → preprocess()` function only uses four raw columns as features: `Age`, `Weight_kg`, `Blood_Pressure`, and `BMI`. The TODO comment notes that several clinically meaningful features are missing because they haven't been engineered yet.

Raw columns are often not the best representation of clinical risk. A 78-year-old patient admitted for 10 days is different from a 78-year-old admitted for 1 day — but both have the same `Age` value. The features below capture information that raw columns alone cannot.

---

## Background

Feature engineering is the process of transforming raw data into representations that better expose the signal a model needs to learn. In healthcare predictive modelling, domain knowledge matters: clinical literature on readmission risk consistently highlights the following factors:

- **Length of Stay (LOS)** — longer stays correlate with higher readmission risk (more complex illness)
- **Insurance status** — uninsured patients often have less follow-up care, increasing risk
- **Hypertension flag** — elevated BP at discharge is a strong readmission predictor for cardiac patients
- **Age group** — elderly patients (80+) have disproportionately high readmission rates; binning captures non-linear age effects better than raw age

---

## Features to Create

Add the following derived columns to `merged_patients.csv` (or create them inside `preprocess()` in the model). Document each feature's definition in a comment.

| Feature | Type | Definition |
|---------|------|------------|
| `Length_of_Stay` | int | `(Discharge_Date - Admission_Date).dt.days` — requires TICKET-001 to be fixed first |
| `Age_Group` | string | Binned age: `'18-40'`, `'41-60'`, `'61-80'`, `'80+'` |
| `Has_Insurance` | int (0/1) | `1` if `Insurance_ID` is not null, `0` otherwise |
| `High_BP` | int (0/1) | `1` if `Blood_Pressure >= 140`, `0` otherwise |

---

## Investigation Steps

1. `Length_of_Stay`: after TICKET-001 is resolved, both date columns will be `datetime64`. How do you subtract two datetime Series in pandas? What dtype does the result have and how do you extract the integer number of days?

2. `Age_Group`: `pd.cut()` takes a `bins=` argument. How do you specify open/closed interval boundaries? What does the `labels=` argument do? What happens to a patient aged exactly 80 — does they fall in `'61-80'` or `'80+'`? Check the `right=` parameter.

3. `Has_Insurance`: this should be 0 or 1 (not True/False). How do you convert a boolean mask to integers in pandas? What is `.astype(int)`?

4. `High_BP`: same pattern as `Has_Insurance`. What happens to rows where `Blood_Pressure` is null? Decide whether to impute (e.g. median) or to propagate NaN, and document your choice.

5. After creating these features, check: are any of the new columns heavily correlated with each other? (A very high correlation between `High_BP` and `Blood_Pressure` is expected — that's by construction. But correlations between `Has_Insurance` and `Department` could indicate a data quality issue worth investigating.)

---

## Acceptance Criteria

- [ ] All four features (`Length_of_Stay`, `Age_Group`, `Has_Insurance`, `High_BP`) are present in the output CSV after running the pipeline
- [ ] `Length_of_Stay` contains only non-negative integers; no rows have a negative LOS
- [ ] `Age_Group` has exactly four categories and no nulls (assuming Age has no nulls)
- [ ] `Has_Insurance` and `High_BP` contain only 0 and 1
- [ ] At least two of the four new features are used in `models/readmission_model.py → preprocess()` in TICKET-007

---

## Relevant Concepts

- `pd.cut()` — bins, labels, right parameter
- `datetime.dt.days` — extracting integer days from a timedelta
- `.astype(int)` and `.notna().astype(int)` for binary flag creation
- Clinical literature on readmission risk factors: Jencks et al. (2009) "Rehospitalizations among Patients in the Medicare Fee-for-Service Program" NEJM — frequently cited benchmark for 30-day readmission research
