# TICKET-010 — Class Imbalance in Readmission Labels

**Priority:** 🟡 LOW / Stretch Goal  
**Type:** Model Improvement  
**Affects:** `models/readmission_model.py → train_model()`, `preprocess()`  
**Prerequisites:** TICKET-007  
**Test:** No automated test — compare classification_report before and after

---

## Problem Description

The `Readmitted_30Day` column has an approximately 85/15 class split — roughly 85 % of patients are not readmitted and 15 % are. This imbalance causes the logistic regression trained in TICKET-007 to learn a biased decision boundary.

Concretely: after training, you will likely find that `model.predict()` rarely or never predicts class 1 (readmitted), because predicting class 0 for every patient still yields ~85 % accuracy. From the confusion matrix:

```
Predicted →     0        1
Actual 0   [  TN  ]  [  FP  ]     (large TN, small FP)
Actual 1   [  FN  ]  [  TP  ]     (large FN, small TP)  ← the problem
```

A model that misses most readmitted patients is clinically useless — the whole point is to identify the 15 % who need intervention.

---

## Background

Class imbalance is one of the most common practical problems in healthcare machine learning. Readmission datasets, fraud detection, rare disease classification — all suffer from it. There are three main approaches:

### Approach A — Cost-sensitive learning
Tell the model to penalise misclassifying the minority class more heavily:

```python
LogisticRegression(class_weight='balanced')
```

`'balanced'` automatically sets class weights inversely proportional to class frequency. This is the simplest fix and a good starting point.

### Approach B — Resampling
Synthetically balance the training set before fitting:

- **Oversampling** (SMOTE): generate synthetic minority-class samples  
  `from imblearn.over_sampling import SMOTE`
- **Undersampling**: randomly remove majority-class samples

Note: resampling is applied only to the **training set**, never to the test set.

### Approach C — Threshold tuning
Logistic regression outputs probabilities. The default 0.5 decision threshold may not be optimal. Lowering it to 0.3 means the model flags a patient as high-risk if there's a 30 % predicted probability rather than 50 %.

```python
y_prob  = model.predict_proba(X_test)[:, 1]
y_pred  = (y_prob >= 0.30).astype(int)
```

This trades precision for recall — you catch more true readmissions but also generate more false alarms.

---

## Investigation Steps

1. Before making any changes, record the baseline confusion matrix and classification_report from TICKET-007. Save these numbers — you'll need them for comparison.

2. Apply Approach A (`class_weight='balanced'`). Re-run the model and compare:
   - Did accuracy go down?
   - Did recall for class 1 (readmitted) go up?
   - What does the trade-off look like in the confusion matrix?

3. Plot a precision-recall curve using `sklearn.metrics.PrecisionRecallCurve`. At what threshold does your model achieve the best balance? What does "best balance" mean clinically — is it more important to avoid missing readmissions or to avoid false alarms?

4. (Optional) If `imblearn` is installed, try SMOTE. Does it outperform `class_weight='balanced'` on this dataset?

5. Summarise your findings: which approach produces the highest recall for the minority class without making precision unacceptably low? Write a 3–5 sentence justification for your final model choice.

---

## Acceptance Criteria

- [ ] At least one of the three approaches (A, B, or C) is implemented and compared against the TICKET-007 baseline
- [ ] The comparison shows both the baseline and improved classification_report
- [ ] Recall for class 1 is higher after the change than before
- [ ] A brief written justification (comment in code or in PR description) explains which approach was chosen and why

---

## Relevant Concepts

- `LogisticRegression(class_weight='balanced')` — sklearn documentation
- `sklearn.metrics.PrecisionRecallCurve` and `sklearn.metrics.average_precision_score`
- `imblearn.over_sampling.SMOTE` — imbalanced-learn library
- Precision-recall trade-off in clinical settings: the cost of a false negative (missed readmission) vs a false positive (unnecessary follow-up call)
- F1 score as a balance metric; F-beta score for weighting recall more heavily than precision
- ROC-AUC vs PR-AUC: why PR-AUC is more informative under class imbalance
