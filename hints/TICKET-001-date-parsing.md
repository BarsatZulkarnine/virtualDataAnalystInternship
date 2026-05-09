# TICKET-001 — Date Parsing Failure in `readmission_report.py`

**Priority:** 🔴 CRITICAL — blocks all downstream report generation  
**Type:** Bug Fix  
**Affects:** `readmission_report.py`, `utils/data_utils.py`  
**Test:** `test_date_parsing_handles_mixed_formats`

---

## Problem Description

Running `python readmission_report.py` raises a `ValueError` and terminates before producing any output:

```
ValueError: time data '03/15/2024' does not match format '%Y-%m-%d'
```

The crash occurs inside `parse_dates()` during the very first step after loading the CSV. Nothing downstream — length of stay calculation, readmission aggregation, chart generation — executes.

---

## Background

The `Discharge_Date` column was sourced from three different systems that were never normalised at ingestion time:

- The **North Wing** EHR exports dates as ISO-8601: `2024-03-15`
- The **South Wing** EHR (Dr. Irfan Sherrif's Cardiology department) exports in US format: `03/15/2024`
- Legacy paper records that were retrospectively digitised used a hybrid format: `15-Mar-2024`

All three formats landed in the same CSV column with no provenance flag.

When asked, Dr. Irfan's response was: *"The system exports whatever it exports. That's an IT problem."* Sakib Rumman from IT said: *"We just pipe the data through, normalisation is the pipeline's job."* So here we are.

This is a common real-world data engineering problem — external systems rarely agree on a date format, and a pipeline that assumes a single format will silently drop or crash on rows from the other systems.

---

## Investigation Steps

1. Open `data/patients.csv` in a text editor or with `df['Discharge_Date'].value_counts()` (sample a few values). Can you identify which formats are present?

2. Look at the current implementation in `readmission_report.py → parse_dates()` and in `utils/data_utils.py → parse_dates_safe()`. What does the `format=` parameter do? What happens when a date string doesn't match?

3. What does `pd.to_datetime()` do when you **omit** the `format=` parameter entirely? Is that safe here? What are the risks of `infer_datetime_format=True`?

4. What does the `errors=` parameter control? What are the three options and what does each one do? Which would let you detect unparseable rows without crashing the whole pipeline?

5. After parsing, how would you verify that no dates became `NaT` (Not a Time)? Write a one-liner assertion or print statement to check this.

6. Update `parse_dates_safe()` in `utils/data_utils.py` first, then update `parse_dates()` in `readmission_report.py` to use it.

---

## Acceptance Criteria

- [ ] `readmission_report.py` runs to completion without raising `ValueError`
- [ ] All 220 rows in the merged dataset have a valid, non-null `Discharge_Date` and `Admission_Date` after parsing
- [ ] `parse_dates_safe()` in `utils/data_utils.py` passes the test `test_date_parsing_handles_mixed_formats` (handles all three formats)
- [ ] If a date truly cannot be parsed, the function logs a warning and returns `NaT` rather than crashing

---

## Relevant Concepts

- `pd.to_datetime()` documentation — particularly the `format`, `errors`, and `dayfirst` parameters
- Python `strftime` / `strptime` format codes: `%Y`, `%m`, `%d`, `%b`
- Difference between `errors='raise'`, `errors='coerce'`, and `errors='ignore'`
- What `NaT` is and how to detect it: `pd.isnull()`, `Series.isna()`
