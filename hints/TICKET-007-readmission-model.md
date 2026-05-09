# TICKET-007 — 30-Day Readmission Prediction Model

**Priority:** 🟠 MEDIUM — core deliverable for Friday  
**Type:** Model Development  
**Affects:** `models/readmission_model.py`  
**Prerequisites:** TICKET-001, TICKET-002, TICKET-003, TICKET-006  
**Test:** No automated test — evaluate using classification_report output

---

## Problem Description

`models/readmission_model.py` is a working scaffold but is incomplete in two ways:

1. `preprocess()` drops all categorical columns (`Department`, `Gender`) instead of encoding them — this discards clinically relevant signal
2. `evaluate_model()` only prints accuracy — which is a misleading metric when the classes are imbalanced (see TICKET-010 for the deeper fix)

---

## Background

Logistic regression is an appropriate baseline for binary classification problems like 30-day readmission. It produces interpretable outputs (log-odds coefficients), trains quickly, and its assumptions are reasonably met here (binary outcome, independent observations, no extreme multicollinearity).

However, a model is only as good as its features and its evaluation. Reporting only accuracy on an 85/15 class split is not sufficient: a model that predicts "no readmission" for every single patient would achieve 85 % accuracy while being completely useless clinically.

---

## What to Build

### Step 1 — Encode categorical features

In `preprocess()`, replace the block that drops categoricals with one-hot encoding:

```python
# Before (drops signal):
feature_cols = ["Age", "Weight_kg", "Blood_Pressure", "BMI"]

# After (encodes categoricals):
df_encoded = pd.get_dummies(df_clean, columns=["Department", "Gender"], drop_first=True)
```

Why `drop_first=True`? Think about what happens if you include a dummy column for every category — what is the relationship between those columns? (This is called the dummy variable trap.)

### Step 2 — Add engineered features

Include the features from TICKET-006 in your feature matrix. At minimum add `Length_of_Stay`, `Has_Insurance`, and `High_BP`.

### Step 3 — Improve evaluate_model()

Replace the accuracy-only output with a full evaluation:

```python
from sklearn.metrics import classification_report, confusion_matrix
```

`classification_report()` prints precision, recall, F1, and support for each class in one call. Understand what each metric means before the Board presentation:

- **Precision** (for class 1 = readmitted): of all patients flagged as readmission risk, how many actually were readmitted?
- **Recall** (for class 1): of all patients who were actually readmitted, how many did the model catch?
- **F1**: harmonic mean of precision and recall — useful when you care about both

### Step 4 — Decision threshold

The default decision threshold in logistic regression is 0.5. In clinical settings, recall (catching true readmissions) is usually more important than precision (avoiding false alarms). Consider whether the default threshold is appropriate or whether it should be lowered. What trade-off does that create?

---

## Investigation Steps

1. Run the existing `train_and_evaluate()` function as-is. What accuracy do you get? What does the confusion matrix look like — how many readmitted patients did the model correctly identify?

2. After adding categorical encoding and engineered features, does performance improve? Compare confusion matrices before and after.

3. Look at the coefficient values: `model.coef_` gives the log-odds weights per feature. Which feature has the largest absolute coefficient? Does that match your intuition from the EDA in TICKET-005?

4. The `stratify=y` parameter in `train_test_split` is already set. Why is this important when classes are imbalanced? What would happen without it?

---

## Acceptance Criteria

- [ ] `preprocess()` one-hot encodes `Department` and `Gender` rather than dropping them
- [ ] The feature matrix includes at least 2 of the engineered features from TICKET-006
- [ ] `evaluate_model()` prints precision, recall, F1, and a confusion matrix
- [ ] The model's recall for the positive class (readmitted = 1) is above 0.20 (random baseline is ~0.15)
- [ ] Code is committed with a brief comment documenting which features were included and why

---

## Relevant Concepts

- `pd.get_dummies()` — `columns`, `drop_first` parameters
- `sklearn.metrics.classification_report()` — reading the output table
- `sklearn.metrics.confusion_matrix()` — TN, FP, FN, TP positions
- Precision-recall trade-off: what it means to lower the decision threshold
- `model.predict_proba()` vs `model.predict()` — when to use each
- Logistic regression coefficients: `model.coef_` and how to interpret them
