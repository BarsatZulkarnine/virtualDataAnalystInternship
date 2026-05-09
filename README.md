# Scholastica General Hospital, Dhaka
## Analytics & Health Informatics Division

---

```
TO:      New Data Analytics Intern
FROM:    Dr. Mushfiq Mahfuz, Lead Health Informatics Engineer
DATE:    2026-05-09
SUBJECT: 30-Day Readmission Pipeline — Handoff & Task Brief
URGENCY: HIGH — Board presentation is this Friday
```

---

Welcome aboard. I'll be direct: this pipeline is broken, and the Board of Directors needs a clean readmission report by **Friday 13 May**. I'm handing this off to you because I'll be at the APAMI conference in Singapore until Thursday.

Some context on how we got here: this pipeline was originally built by **Barsat Zulkarnine**, our former Senior Data Engineer, before he transferred to the Singapore branch earlier this year. Barsat is brilliant but was under serious deadline pressure and, by his own admission, "shipped fast and documented never." We love him anyway.

Since then, **Sakib Rumman** (IT Systems Architect) and **Irfan Sherrif** (Head of Cardiology) have both made undocumented changes to the data ingestion layer, which is part of why the date formats are now a disaster. Neither of them will admit responsibility. Classic.

Your job is to find the bugs, fix them, and extend the pipeline to include a basic readmission risk model. Everything you need is in this repository — including some very pointed hints.

---

## Background

Scholastica General Hospital tracks 30-day readmission rates as a core quality metric — hospitals with high readmission rates face CMS penalty adjustments. The Board wants to know:

1. Which departments have the highest readmission rates?
2. Are there identifiable patient characteristics that predict readmission?
3. Which patients currently in the system should be flagged as high priority?

---

## Repository Layout

```
readmission-pipeline/
├── patient_data_gen.py      ← Run first. Generates patients.csv and visits.sqlite
├── analytics_pipeline.py    ← Joins CSV + SQLite, computes BMI. CONTAINS BUGS
├── readmission_report.py    ← Generates Plotly dashboard. CRASHES on startup
│
├── utils/
│   ├── data_utils.py        ← Helper functions (several are stubs — see tickets)
│   └── validation.py        ← Data quality checks (these work correctly)
│
├── models/
│   └── readmission_model.py ← Logistic regression scaffold (incomplete)
│
├── tests/
│   ├── test_ticket_001_date_parsing.py
│   ├── test_ticket_002_bmi_height.py
│   ├── test_ticket_003_merge.py
│   ├── test_ticket_004_bp_flagging.py
│   ├── test_ticket_005_eda.py
│   ├── test_ticket_006_features.py
│   ├── test_ticket_007_model.py
│   ├── test_ticket_008_deduplication.py
│   ├── test_ticket_009_dashboard.py
│   └── test_ticket_010_class_imbalance.py
│
├── config.py                ← All paths and thresholds in one place
├── data/                    ← Generated data lands here (gitignored)
├── reports/                 ← HTML dashboard output — open in any browser
└── hints/                   ← Ticket-by-ticket guidance (start here)
```

---

## Known Issues

The following issues were discovered before I left. Each has a corresponding ticket in `hints/`:

| # | Severity | Issue |
|---|----------|-------|
| TICKET-001 | 🔴 CRITICAL | **Pipeline crashes on date conversion.** `readmission_report.py` raises `ValueError` immediately because `Discharge_Date` contains rows in three different string formats and the parser only handles one. Nothing downstream runs until this is fixed. |
| TICKET-002 | 🔴 HIGH | **BMI numbers look physically impossible.** Some patients are showing BMI values above 800. This is caused by two compounding errors — a formula bug AND a unit inconsistency in the height column. |
| TICKET-003 | 🟠 HIGH | **~30 % of patients disappear after the merge.** The join logic drops every patient who doesn't have an Insurance_ID. We cannot submit a report to the Board that excludes uninsured patients. |
| TICKET-008 | 🟠 HIGH | **Duplicate patient records with conflicting blood pressure readings.** About 10 % of Patient_IDs appear twice with different BP values. We need a consistent deduplication policy before any risk scoring is meaningful. |

---

## Your Task List

Work through the tickets in `hints/` in the order below. Each ticket explains the problem, gives you investigation pointers, and defines acceptance criteria. The test suite (`pytest tests/ -v`) will tell you objectively when each fix is correct.

### Phase 1 — Fix the Pipeline (Blocking)
- [ ] **TICKET-001** — Fix date parsing so the report can run at all
- [ ] **TICKET-002** — Fix the BMI formula and height unit normalisation
- [ ] **TICKET-003** — Fix the patient merge so no records are lost
- [ ] **TICKET-008** — Resolve duplicate patient records (document your strategy)

### Phase 2 — Data Quality & Exploration
- [ ] **TICKET-004** — Add blood pressure risk stratification column
- [ ] **TICKET-005** — Perform exploratory data analysis on the patient population

### Phase 3 — Feature Engineering & Modelling
- [ ] **TICKET-006** — Engineer the readmission risk features
- [ ] **TICKET-007** — Train the logistic regression readmission model
- [ ] **TICKET-009** — Produce the final readmission visualisation dashboard
- [ ] **TICKET-010** — (Stretch) Address class imbalance in the model

---

## Getting Started

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
```

## Running the Pipeline

Run these steps in order. Each step depends on the previous one.

```bash
# Step 1 — Generate synthetic patient data  (run ONCE — files persist on disk)
python patient_data_gen.py
#   Produces: data/patients.csv    (~2,400 rows with intentional data quality issues)
#             data/visits.sqlite   (6,000 visit records)
#   Only rerun if you delete the data/ folder or are told to reset.

# Step 2 — Run the analytics pipeline
python analytics_pipeline.py
#   Produces: data/merged_patients.csv
#   Will print BMI warnings — that is expected and part of TICKET-002.

# Step 3 — Generate the readmission report
python readmission_report.py
#   Produces: reports/readmission_by_department.html
#   The browser will open automatically when the script finishes.
#   !! This script CRASHES before producing any output — fix TICKET-001 first !!

# Step 4 — Train the readmission model (after Phase 1 bugs are fixed)
python -m models.readmission_model
```

## Tracking Your Progress with Tests

Each ticket has a dedicated test file. Run just the file you are currently working on:

```bash
# Run all tests (65 total — most will fail at the start)
pytest tests/ -v

# Run only the tests for the ticket you are working on
pytest tests/test_ticket_001_date_parsing.py -v
pytest tests/test_ticket_002_bmi_height.py -v
# ... and so on

# Quick pass/fail summary without verbose output
pytest tests/ -q
```

A test passing means the acceptance criteria for that ticket are met. **Do not modify the test files** — they are the ground truth for this assignment.

---

## A Note on Resources

The `hints/` folder contains structured guidance for every ticket. Use it.

**Do not use AI assistants to generate solutions for this assignment.** The point is for you to demonstrate that you can read a broken pipeline, form hypotheses, test them, and arrive at correct fixes through investigation. The hints are calibrated to give you direction without giving away the answer.

If you get genuinely stuck on something after reading the relevant ticket and spending 30+ minutes on it, send me a message and I will reply when I land. You can also ask Irfan or Sakib, but don't expect them to admit anything.

Good luck — the Board is counting on us. Barsat would want you to succeed too, probably.

— Dr. Mushfiq Mahfuz
Lead Health Informatics Engineer, Scholastica General Hospital, Dhaka
