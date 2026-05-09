# Hints — How to Use This Folder

Each file in this folder is a structured ticket corresponding to a bug fix, feature, or analysis task in the readmission pipeline. They are written the same way our team writes internal Jira tickets.

---

## Ticket Format

Every ticket contains:

- **Priority** — how urgently this needs to be done
- **Affected Files** — which scripts to look at
- **Problem Description** — what's observed (symptoms, not cause)
- **Background** — clinical or technical context that explains *why* this matters
- **Investigation Steps** — guiding questions to help you locate the root cause; these are prompts, not answers
- **Acceptance Criteria** — the definition of "done"; the test suite enforces these
- **Relevant Concepts** — pandas / sklearn documentation links and references you may find helpful

---

## Recommended Reading Order

```
Phase 1 (blocking — pipeline won't run without these)
├── TICKET-001-date-parsing.md
├── TICKET-002-unit-inconsistency.md
├── TICKET-003-data-loss-join.md
└── TICKET-008-duplicate-records.md

Phase 2 (data quality + exploration)
├── TICKET-004-bp-risk-flagging.md
└── TICKET-005-eda-demographics.md

Phase 3 (feature engineering + modelling)
├── TICKET-006-feature-engineering.md
├── TICKET-007-readmission-model.md
├── TICKET-009-visualization-dashboard.md
└── TICKET-010-class-imbalance.md   ← stretch goal
```

---

## A Note on Process

Reading a ticket carefully is not optional — it exists so you don't spend three hours chasing the wrong hypothesis. That said, the hints will not write the code for you. They are calibrated to close the distance between "I have no idea where to start" and "I know exactly what to look at next."

If a ticket references a concept you haven't encountered before (e.g. class imbalance, left join semantics), that's intentional — part of the assignment is doing the background reading.
