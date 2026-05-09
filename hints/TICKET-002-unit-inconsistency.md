# TICKET-002 — Physically Impossible BMI Values

**Priority:** 🔴 HIGH — all risk scoring and reporting downstream is invalid  
**Type:** Bug Fix (two compounding errors)  
**Affects:** `analytics_pipeline.py`, `utils/data_utils.py`  
**Test:** `test_bmi_calculation_known_value`, `test_bmi_in_plausible_range`

---

## Problem Description

After running `analytics_pipeline.py`, the BMI column contains values ranging from approximately 40 to over 4,000. A normal adult BMI sits between 15 and 40. Values above 60 are medically implausible and indicate a data or formula error.

The `validate_bmi_range()` function in `utils/validation.py` will flag these rows with:

```
[WARN] 952 rows (63.5%) have BMI outside [10, 60].  Observed range: 40.3 – 4218.7
```

---

## Background

BMI is a standard clinical screening metric:

```
BMI = weight_kg / (height_m)²
```

When confronted with BMI values above 800, Barsat Zulkarnine (who wrote the original formula) responded via Slack from Singapore: *"lol that can't be right, must be a data issue."* It is, in fact, both.

Two separate errors in the pipeline are compounding to produce impossible values:

**Error A — Formula bug:**  
The implementation in `analytics_pipeline.py → calculate_bmi()` is missing the exponent. A 70 kg patient at 1.75 m should produce BMI ≈ 22.9. The current formula produces 40.0 (70 / 1.75). This alone makes every value ~1.75× too large, but not dramatically wrong.

**Error B — Unit mismatch:**  
The `Height` column in `patients.csv` contains a mix of values: approximately 70 % are in centimetres (typical range 152–196) and 30 % are in inches (typical range 59–79). The pipeline divides all values by 100 assuming they are centimetres. For an inch-valued row of 65 inches, this produces `height_m = 0.65 m` — a nonsensically short patient — which then explodes the BMI denominator.

When both errors apply to the same row, the result is a BMI in the hundreds or thousands.

---

## Investigation Steps

1. Look at the raw `Height` column in `patients.csv`. Plot a histogram or call `df['Height'].describe()`. Do you see a bimodal distribution? What would the two peaks represent?

2. What is the typical range for adult height in centimetres? In inches? Is there a clear threshold you could use to separate the two populations? Think carefully about edge cases — can a valid cm value overlap with a valid inch value?

3. Open `analytics_pipeline.py` and find the `calculate_bmi()` function. Verify by hand: for weight=70, height=1.75, what does the current formula return? What should it return? What is the fix?

4. Now look at `utils/data_utils.py → normalize_height()`. The TODO comment describes what is missing. What check would you add to detect which rows are in inches before dividing by 100? (Hint: 1 inch = 2.54 cm)

5. After fixing both issues, run `validate_bmi_range()` on the output. Do all BMI values fall within [10, 60]?

---

## Acceptance Criteria

- [ ] `test_bmi_calculation_known_value` passes: `calculate_bmi(70, 1.75)` returns a value within 0.1 of 22.86
- [ ] `test_bmi_in_plausible_range` passes: BMI is in [10, 60] for all test cases
- [ ] `normalize_height()` in `utils/data_utils.py` converts inch rows to centimetres before the division
- [ ] After a full pipeline run, `validate_bmi_range()` prints `[OK]` — no out-of-range values
- [ ] Your fix does not hard-code row indices — it must work on any dataset with the same mixed-unit pattern

---

## Relevant Concepts

- Unit conversion: 1 inch = 2.54 cm; typical adult ranges (cm: 150–200, inches: 59–79)
- `numpy.where()` or `pandas.Series.apply()` for conditional column transformations
- Histogram visualisation to spot bimodal distributions: `df['Height'].hist(bins=50)`
- Defensive programming: what happens if a future batch contains only cm values? Does your detection logic still work?
