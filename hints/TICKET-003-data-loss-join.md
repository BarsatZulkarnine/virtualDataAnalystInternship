# TICKET-003 — Patient Count Drops After Data Merge

**Priority:** 🔴 HIGH — report excludes ~30 % of patients  
**Type:** Bug Fix  
**Affects:** `analytics_pipeline.py → merge_datasets()`  
**Test:** `test_no_patients_lost_after_merge`

---

## Problem Description

`analytics_pipeline.py` prints the following after the merge step:

```
Pre-merge  patient rows : 220
Post-merge rows         : ~154
[!] 46 patient IDs have no match in visit records.
```

The Board report must cover **all** patients admitted to St. Gemini Memorial. A report that silently excludes 30 % of the patient population — without any annotation explaining why — is not acceptable for a quality audit submission.

---

## Background

The merge was written to join patient demographics with billing visit records using `Insurance_ID` as one of the join keys. The intent was to link each patient to their billing insurer for cost analysis.

However, approximately 30 % of patients at St. Gemini Memorial are uninsured or self-pay. Their `Insurance_ID` field in `patients.csv` is `NULL`. When a SQL-style `INNER JOIN` is performed on a column that contains `NULL`, those rows are dropped entirely — `NULL` does not equal `NULL` in join semantics.

This is a silent data loss: the script does not raise an error, it just returns fewer rows.

---

## Investigation Steps

1. Before touching any code, quantify the problem. Add two print statements to `merge_datasets()`:
   - How many patients have a `NULL` Insurance_ID in the raw CSV?  
     `patients['Insurance_ID'].isna().sum()`
   - What percentage is that of total patients?

2. Compare the pre- and post-merge counts. Is the drop in patient count consistent with the number of uninsured patients?

3. Look at the `how=` parameter in `pd.merge()`. What are the four options (`inner`, `left`, `right`, `outer`) and what does each one preserve? Which one should be used here to keep all patients regardless of whether they have an insurance match?

4. After changing the join type, check: do patients with `NULL` Insurance_ID now appear in the merged dataset? What value do their visit-related columns contain? Is that acceptable?

5. Consider whether `Insurance_ID` should even be a join key. What is the correct primary join key between patients and visits? Is it possible that a patient has visits but their insurance changed between admissions?

---

## Acceptance Criteria

- [ ] `test_no_patients_lost_after_merge` passes: the number of unique Patient_IDs in the merged dataset equals the number of unique Patient_IDs in the source CSV
- [ ] Patients with `NULL` Insurance_ID are present in the output with `NaN` in visit-related columns (not dropped)
- [ ] The fix uses the correct join type; do not work around the problem by pre-filtering NULLs

---

## Relevant Concepts

- `pandas.merge()` — the `how=` parameter and what each join type does
- SQL NULL semantics in join conditions: why `NULL = NULL` is false
- Left join vs inner join: when to use each, and their implications for data completeness
- The difference between "no insurance record" and "patient does not exist"
