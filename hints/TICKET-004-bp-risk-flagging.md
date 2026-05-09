# TICKET-004 — Blood Pressure Risk Stratification

**Priority:** 🟠 MEDIUM — required for Board summary slide  
**Type:** Feature  
**Affects:** `utils/data_utils.py → flag_blood_pressure()`, `analytics_pipeline.py`  
**Test:** `test_bp_flagging_returns_correct_tiers`

---

## Problem Description

`flag_blood_pressure()` in `utils/data_utils.py` is a stub that returns `None` for every row. As a result, `analytics_pipeline.py` cannot produce the `Risk_Flag` column that the readmission report and the Board summary depend on.

The test `test_bp_flagging_returns_correct_tiers` currently fails with:

```
AssertionError: flag_blood_pressure() returned None — function not yet implemented.
```

---

## Background

Blood pressure classification is standardised by the American Heart Association (AHA). For this pipeline we are using a simplified three-tier model aligned with clinical triage guidelines:

| Systolic BP (mmHg) | Risk Tier | Clinical Meaning |
|--------------------|-----------|-----------------|
| ≥ 140 | **High Priority** | Hypertensive — requires immediate clinical review |
| 90 – 139 | **Moderate** | Monitor; follow up at next visit |
| < 90 | **Monitor** | Hypotensive or borderline — also requires review |
| NULL / NaN | NaN | Missing reading — do not assign a tier |

Note the boundary at 140: a reading of exactly 140 mmHg should be classified as **High Priority** (≥, not >).

The `Risk_Flag` column produced here feeds into:
- The executive dashboard (how many patients are High Priority per department?)
- TICKET-007 (logistic regression feature: `High_BP`)
- TICKET-009 (dashboard segmentation by risk tier)

---

## Investigation Steps

1. Look at the function signature and docstring in `utils/data_utils.py`. The expected input is a `pd.Series` of integer systolic BP values (with possible NaN). The expected output is a `pd.Series` of string labels.

2. Two common pandas approaches for this kind of conditional mapping:
   - `pd.cut(series, bins=[...], labels=[...])` — useful when bins are contiguous numeric ranges
   - `numpy.select(condlist, choicelist, default=...)` — useful when conditions are more complex

   Which one handles `NaN` inputs more naturally? Try both if you're unsure.

3. Verify boundary behaviour manually before writing the implementation:
   - BP = 140 → should return `'High Priority'`
   - BP = 139 → should return `'Moderate'`
   - BP = 90  → should return `'Moderate'`
   - BP = 89  → should return `'Monitor'`

4. What should happen when the input is `NaN`? Your function must return `NaN` (not the string `'None'` or `'NaN'`) to signal a missing reading. Test this explicitly.

5. After implementing the function, add a call in `analytics_pipeline.py → run_pipeline()` to apply it and create a `Risk_Flag` column in the merged DataFrame before saving to CSV.

---

## Acceptance Criteria

- [ ] `test_bp_flagging_returns_correct_tiers` passes (all boundary cases correct, NaN preserved)
- [ ] `flag_blood_pressure()` returns a `pd.Series`, not a list or scalar
- [ ] NaN inputs produce NaN outputs (not a string)
- [ ] `analytics_pipeline.py` writes a `Risk_Flag` column to `merged_patients.csv`

---

## Relevant Concepts

- `pd.cut()` — `bins`, `labels`, `right` parameters; how it handles values outside the bin range
- `numpy.select()` — building condition arrays, default value
- Pandas NaN propagation: why `np.nan` comparisons require `pd.isna()` rather than `== np.nan`
- AHA Blood Pressure Categories: https://www.heart.org/en/health-topics/high-blood-pressure/understanding-blood-pressure-readings
