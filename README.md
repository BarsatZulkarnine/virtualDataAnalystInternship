# St. Gemini Memorial Hospital
## Analytics & Health Informatics Division

---

```
TO:      New Data Analytics Intern
FROM:    Dr. Sarah Chen, Lead Health Informatics Engineer
DATE:    2026-05-09
SUBJECT: 30-Day Readmission Pipeline — Handoff & Task Brief
URGENCY: HIGH — Board presentation is this Friday
```

---

Welcome aboard. I'll be direct: this pipeline is broken, and the Board of Directors needs a clean readmission report by **Friday 13 May**. I'm handing this off to you because I'll be at the HIMSS conference until Thursday.

The good news is that the architecture is sound and the data is already being generated. The bad news is that several bugs were introduced during rapid prototyping, and I did not have time to clean them up before travelling.

Your job is to find them, fix them, and extend the pipeline to include a basic readmission risk model. Everything you need is in this repository.

---

## Background

St. Gemini Memorial tracks 30-day readmission rates as a core quality metric — hospitals with high readmission rates face CMS penalty adjustments. The Board wants to know:

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
│   └── test_pipeline.py     ← 7 tests; most will FAIL until you fix the bugs
│
├── config.py                ← All paths and thresholds in one place
├── data/                    ← Generated data lands here (gitignored)
├── reports/                 ← HTML report output
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

## Running the Pipeline

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate synthetic data
python patient_data_gen.py

# 4. Run the analytics pipeline (will print warnings about BMI — that's expected)
python analytics_pipeline.py

# 5. Run the report generator (will crash — see TICKET-001)
python readmission_report.py

# 6. Run the test suite to track your progress
pytest tests/test_pipeline.py -v
```

---

## A Note on Resources

The `hints/` folder contains structured guidance for every ticket. Use it.

**Do not use AI assistants to generate solutions for this assignment.** The point is for you to demonstrate that you can read a broken pipeline, form hypotheses, test them, and arrive at correct fixes through investigation. The hints are calibrated to give you direction without giving away the answer.

If you get genuinely stuck on something after reading the relevant ticket and spending 30+ minutes on it, send me a message and I will reply when I land.

Good luck — the Board is counting on us.

— Dr. Sarah Chen
Lead Health Informatics Engineer, St. Gemini Memorial
