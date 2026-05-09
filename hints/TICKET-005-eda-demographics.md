# TICKET-005 — Exploratory Data Analysis: Patient Population Profiling

**Priority:** 🟠 MEDIUM — required before any modelling  
**Type:** Analysis Task  
**Affects:** New notebook or script (your choice); `data/merged_patients.csv`  
**Test:** No automated test — deliverable is a saved EDA report or notebook

---

## Problem Description

No one on the team has done a structured EDA on this dataset yet. Before we fit any models or draw conclusions for the Board, we need to understand the population we are working with. Modelling on data you haven't looked at produces models you cannot explain or trust.

---

## Background

Exploratory Data Analysis (EDA) for a clinical dataset serves two purposes:

1. **Data quality audit** — surfacing distributions that reveal upstream errors (impossible values, missing data patterns, suspicious outliers)
2. **Feature relevance screening** — identifying which variables appear to correlate with the outcome (readmission) before committing to a feature set for modelling

In a healthcare context, EDA findings also have clinical meaning. A spike in readmissions in the Cardiology department, or a bimodal age distribution in Oncology patients, are observations a clinician would want to investigate. Your job is to produce the analysis — the clinical team interprets the findings.

---

## Analysis Checklist

Complete all of the following. Save your output to `reports/eda_summary.ipynb` or `reports/eda_summary.html`.

### 1. Data overview
- Shape, dtypes, null counts per column
- Percentage of rows with at least one null value
- How many unique patients? How many have duplicate Patient_IDs?

### 2. Demographic distributions
- Age distribution (histogram with KDE overlay) — overall and by Department
- Gender split (bar chart or pie) — overall and by Department
- Is the age distribution consistent across departments, or does one department skew older/younger?

### 3. Clinical variable distributions
- Blood Pressure: histogram, identify what percentage fall in each AHA tier
- BMI: histogram after fixing TICKET-002 — does the distribution look plausible?
- Length of Stay: histogram — is there a long tail? Any stays > 30 days?

### 4. Readmission analysis
- Overall readmission rate (value_counts + bar chart)
- Readmission rate by Department (grouped bar chart)
- Readmission rate by Gender
- Readmission rate by Age Group (bin into: 18–40, 41–60, 61–80, 80+)
- What diagnosis codes appear most frequently among readmitted patients?

### 5. Correlation analysis
- Compute a Pearson correlation matrix for all numeric features
- Visualise as an annotated heatmap (seaborn `heatmap`)
- Which features correlate most strongly with `Readmitted_30Day`?
- Are any predictor features strongly correlated with each other (multicollinearity risk)?

### 6. Missing data pattern
- Visualise which columns have nulls and whether missingness is random or systematic
- Is `Insurance_ID` null for specific departments? Specific diagnoses? Or randomly distributed?

---

## Acceptance Criteria

- [ ] EDA notebook / script runs end to end without errors on `data/merged_patients.csv`
- [ ] All 6 analysis sections above are addressed with at least one visualisation each
- [ ] Plots are labelled (title, axis labels, units)
- [ ] A written summary section (2–4 bullet points) describes the most important findings
- [ ] Results are saved to `reports/`

---

## Relevant Concepts

- `df.describe()`, `df.info()`, `df.isna().sum()`
- `seaborn.histplot()`, `seaborn.boxplot()`, `seaborn.heatmap()`
- `df.groupby().agg()` for computing readmission rates per group
- `pd.cut()` for creating age bins
- Pearson correlation: `df.corr()` — what a value close to 1, -1, and 0 means
- Multicollinearity: why two highly correlated predictors in the same model can cause problems
