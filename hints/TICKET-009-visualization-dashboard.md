# TICKET-009 — Readmission Rate Visualization Dashboard

**Priority:** 🟠 MEDIUM — the Board's primary deliverable  
**Type:** Visualization  
**Affects:** `readmission_report.py`  
**Prerequisites:** TICKET-001 (date parsing), TICKET-004 (Risk_Flag column)  
**Test:** No automated test — deliverable is `reports/readmission_by_department.html`

---

## Problem Description

The Board presentation requires a clear visual summary of readmission patterns across the hospital. Once TICKET-001 is resolved and the report script can run, it only generates one chart. The Board slide deck needs three distinct views:

1. Readmission rate by **Department**
2. Readmission rate by **Risk Tier** (`Risk_Flag` column from TICKET-004)
3. Readmission rate by **Age Group** (`Age_Group` column from TICKET-006)

---

## Background

Plotly Express is already a dependency. Interactive HTML charts are preferred over static PNGs because the Board members will explore the data during the Q&A session (filtering, hovering for exact percentages).

A chart is only as good as its labelling. Every chart delivered to a clinical audience must have:
- A descriptive title that includes the hospital name and the metric being shown
- Axis labels with units
- Hover tooltips that show both the rate (%) and the patient count
- A note on the time period covered (use the Admission_Date range from the dataset)

---

## Charts to Build

### Chart 1 — Readmission Rate by Department (already scaffolded)
The skeleton exists in `readmission_report.py → generate_department_chart()`. Make sure it runs after TICKET-001 is fixed and includes patient count in the hover tooltip.

### Chart 2 — Readmission Rate by Risk Tier

```python
# Expected output columns from compute_readmission_rates() grouped by Risk_Flag:
# Risk_Flag | Total_Patients | Readmission_Rate_Pct
```

Sort the bars by clinical priority order: `['High Priority', 'Moderate', 'Monitor']`. Use red/amber/green colouring. Does the data show what you'd expect — do High Priority patients have higher readmission rates?

### Chart 3 — Readmission Rate by Age Group

Group by the `Age_Group` column created in TICKET-006. Do older patients have higher readmission rates? Is the relationship monotonically increasing, or is there a non-linear pattern?

### Bonus — Combined subplot

Combine all three charts into a single HTML file using `plotly.subplots.make_subplots()`. This produces one self-contained file that can be attached to an email.

---

## Investigation Steps

1. Confirm that `Risk_Flag` and `Age_Group` columns exist in `merged_patients.csv` before attempting to group by them. Add a check at the top of `run_report()`.

2. For the colour scheme on Chart 2, `plotly.express` accepts a `color_discrete_map` parameter that maps category names to hex colours. How would you assign red to 'High Priority', amber to 'Moderate', and green to 'Monitor'?

3. Look at the hover template in Chart 1. What does `%{customdata[0]}` refer to? How do you add the patient count to the tooltip?

4. What does `fig.write_html()` produce? Can you open it in a browser directly without a server? Test this after generating it.

---

## Acceptance Criteria

- [ ] `readmission_report.py` runs end-to-end and produces at least two charts in `reports/`
- [ ] Each chart has a title, labelled axes, and unit annotations
- [ ] Charts use `fig.write_html()` output — no static PNG for the Board deliverable
- [ ] Chart 2 (by Risk Tier) uses clinically intuitive colour coding (red for High Priority)
- [ ] The report prints a summary table to stdout showing the raw numbers behind each chart

---

## Relevant Concepts

- `plotly.express.bar()` — `color`, `color_discrete_map`, `hover_data`, `text` parameters
- `plotly.subplots.make_subplots()` — combining multiple charts in one figure
- `fig.update_traces(texttemplate=...)` — formatting bar labels
- `fig.write_html(include_plotlyjs='cdn')` — produces a smaller file that loads Plotly from CDN
- Data visualisation best practice for clinical audiences: keep it simple, use colour purposefully, always show N (patient count) alongside percentages
