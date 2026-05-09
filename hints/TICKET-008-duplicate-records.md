# TICKET-008 — Conflicting Records for the Same Patient

**Priority:** 🟠 HIGH — affects risk scoring and Board-level counts  
**Type:** Data Quality / Decision  
**Affects:** `analytics_pipeline.py`, `utils/data_utils.py → deduplicate_patients()`  
**Test:** `test_duplicate_detection`

---

## Problem Description

Running `check_for_duplicates(patients, 'Patient_ID')` on the raw CSV reveals:

```
[WARN] 40 rows share a non-unique 'Patient_ID' (20 distinct IDs affected).
       Examples: ['SGH-00043', 'SGH-00091', 'SGH-00017', ...]
```

Twenty patient IDs appear twice — once with a blood pressure reading from one source system and once with a different reading from another. Until this is resolved, any BP-based risk stratification (TICKET-004) or BP features in the model (TICKET-007) will be inconsistent depending on which row a downstream operation happens to use.

---

## Background

Duplicate patient records are one of the most common and consequential data quality problems in healthcare analytics. They arise when:

- A patient is registered in two different ward systems with the same ID
- A record is exported twice due to an ETL bug
- A patient re-presents and a new admission is created rather than linked to the existing record

In this case, the likely cause is that Irfan's Cardiology department and the General Medicine department both export patient records independently, and a subset of patients who visited both departments ended up registered twice. Dr. Irfan disputes this. The IT logs suggest otherwise.

In clinical settings, the *consequence* of using the wrong record varies. For blood pressure, the choice matters:

- Using the **most recent** reading assumes the patient's condition has evolved and the latest value is most current
- Using the **highest** reading is the conservative/safety-first approach — it ensures no high-risk patient is accidentally downgraded to Moderate
- Using the **first** reading preserves the original admission data, which may be most relevant for readmission risk (the patient's condition at admission, not discharge)

There is no universally correct answer. This is a **clinical policy decision** that must be documented and justified.

---

## Investigation Steps

1. Use `check_for_duplicates()` from `utils/validation.py` to quantify the problem. How many rows are affected? Are the duplicate rows identical except for Blood_Pressure, or do other columns also differ?

2. For a sample of duplicate Patient_IDs, look at both rows side-by-side:
   ```python
   dup_ids = patients[patients.duplicated('Patient_ID', keep=False)]['Patient_ID'].unique()
   patients[patients['Patient_ID'] == dup_ids[0]]
   ```
   How different are the BP values? Are both clinically plausible, or does one look like a data entry error?

3. Consider the three deduplication strategies:
   - `keep='first'` (current stub) — what does "first" mean in an unsorted CSV?
   - Keep the row with the highest `Blood_Pressure` — implement using `groupby + idxmax`
   - Keep the most recent row by `Admission_Date` — requires parsing dates first

4. Whichever strategy you choose, document it: add a one-line comment in `deduplicate_patients()` and mention it in your PR description.

5. After deduplication, verify the result: `df['Patient_ID'].nunique()` should equal `df.shape[0]` — every ID appears exactly once.

---

## Acceptance Criteria

- [ ] `test_duplicate_detection` passes (the validation helper correctly identifies duplicates)
- [ ] `deduplicate_patients()` in `utils/data_utils.py` has a documented deduplication strategy (comment in code)
- [ ] After calling `deduplicate_patients()`, there are zero duplicate Patient_IDs in the output
- [ ] The chosen strategy is mentioned in the commit message or PR description with a one-sentence justification

---

## Relevant Concepts

- `df.duplicated(subset, keep=False)` — identifying all rows involved in a duplication
- `df.groupby('Patient_ID').apply(...)` — applying custom logic per group
- `df.sort_values(...).drop_duplicates(keep='last')` — date-based deduplication
- `df.groupby('Patient_ID')['Blood_Pressure'].idxmax()` — row-level argmax within groups
- Master Patient Index (MPI): the healthcare informatics concept of a canonical patient identity record
