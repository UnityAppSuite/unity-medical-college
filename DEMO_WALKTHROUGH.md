# Unity Medical College — Demo Walkthrough

**Date**: March 2026  
**Duration**: ~30 minutes  
**Audience**: University registrars, medical college deans, academic administrators  
**Live Demo URL**: http://209.182.233.131:8000

---

## Demo Credentials

| Role | Email | Password | Dashboard |
|------|-------|----------|-----------|
| **Administrator** | Administrator | 12345 | Full access |
| **Dean** | dean@dypatil.edu | DyPatil@2025Demo | http://209.182.233.131:8000/app/dean-dashboard |
| **Registrar** | registrar@dypatil.edu | DyPatil@2025Demo | http://209.182.233.131:8000/app/registrar-dashboard |

---

## Pre-Demo Setup (Already Done on Live Server)

The following is already configured on the live demo server:

```bash
# App is installed
bench --site walnut install-app unity_medical_college

# Demo data is seeded (Medical College Settings enabled, NMC data loaded)
# Medical College Settings: enable_medical_module = 1
# Institution: D.Y. Patil University School of Medicine
```

If resetting from scratch:
```bash
cd ~/frappe-bench
bench get-app https://github.com/UnityAppSuite/unity-medical-college
bench --site walnut install-app unity_medical_college
bench --site walnut execute unity_medical_college.medical_demo_data.seed_demo_data
bench --site walnut clear-cache
```

---

## Walkthrough Script

### Act 1: Introduction (2 min)

**Login** as Administrator  
→ http://209.182.233.131:8000/login

**Talking points:**
- Unity Medical College is a standalone Frappe addon adding NMC-compliant medical college management
- Installs alongside the core University App — shares student, faculty, and department records
- Feature-flag gated: enable/disable without touching the base system

---

### Act 2: Enable the Medical Module (2 min)

1. Go to **Medical College Settings**  
   → http://209.182.233.121:8000/app/medical-college-settings

2. Show the settings panel:
   - **Enable Medical Module** ✓ (already on)
   - **Institution Name**: D.Y. Patil University School of Medicine
   - **Regulatory Body**: NMC
   - **Theory Attendance Threshold**: 75% (NMC MSR 2023)
   - **Clinical Attendance Threshold**: 75%
   - **Feature Flags**: Curriculum Map ✓ | Case Logs ✓ | OSCE ✓

**Key message**: _"One toggle. When off, all medical features gracefully disappear. When on, the full MBBS workflow activates."_

---

### Act 3: Medical Dean Dashboard (10 min)

→ http://209.182.233.131:8000/app/medical-dean-dashboard

#### KPI Cards

| KPI | What it shows | NMC Reference |
|-----|--------------|---------------|
| **Student Eligibility Rate** | % of students meeting attendance thresholds to sit exams | MSR 2023: Theory ≥75%, Clinical ≥80% |
| **Attendance Defaulters** | Students below NMC threshold (red if any) | Students at risk of exam bar |
| **Faculty NMC Compliance** | % of departments meeting faculty strength norms | MSR 2023 faculty-student ratios |
| **Theory Exam Pass %** | Theory exam pass rate across all components | NMC pass mark: 50% |
| **Practical Pass %** | Practical/clinical exam pass rate | NMC pass mark: 50% |
| **Curriculum Coverage** | Sessions delivered vs planned (CBME) | CBME curriculum completion |

#### Charts

- **Batch/Phase Distribution** — Students across MBBS Phase 1 / 2 / 3A / 3B / Internship
- **Attendance Defaulters by Department** — Which departments have at-risk students
- **Exam Component Pass Rates** — Theory vs Practical vs Viva vs Overall
- **CBME Case Log Completion** — Submitted vs pending case logs

**Key message**: _"Single-screen NMC compliance view — everything needed for accreditation readiness."_

---

### Act 4: Clinical Coordinator Dashboard (5 min)

→ http://209.182.233.131:8000/app/clinical-coordinator-dashboard

Walk through:
- Active clinical postings by department
- Case log submission tracking
- OSCE assessment results
- Student rotation status

**Key message**: _"Day-to-day clinical operations — rotations, case logs, OSCE — all tracked in real-time."_

---

### Act 5: Browse Medical Records (5 min)

| DocType | URL | What to show |
|---------|-----|-------------|
| **Clinical Postings** | http://209.182.233.131:8000/app/mbbs-clinical-posting | Student rotations, attendance %, department, status |
| **Case Logs** | http://209.182.233.131:8000/app/mbbs-case-log | Patient cases: complaint, diagnosis, case type, supervisor verified |
| **OSCE Assessments** | http://209.182.233.131:8000/app/mbbs-osce-assessment | 5 stations × 20 marks each |
| **Exam Components** | http://209.182.233.131:8000/app/mbbs-exam-component | Theory / Practical / Viva independent pass/fail |
| **NMC Faculty Compliance** | http://209.182.233.131:8000/app/nmc-faculty-compliance | Required vs actual faculty per dept (3 depts with shortfall) |
| **Curriculum Maps** | http://209.182.233.131:8000/app/curriculum-map | Planned sessions per course (CBME) |
| **Teaching Records** | http://209.182.233.131:8000/app/teaching-record | Actual sessions delivered (~80% coverage) |

---

### Act 6: Integration with University App (3 min)

1. **Dean Dashboard** (base university features alongside medical)  
   → http://209.182.233.131:8000/app/dean-dashboard

2. **Student record** — same student in both enrollment (university_app) and medical module (postings, case logs, OSCE)  
   → http://209.182.233.131:8000/app/student

**Key message**: _"One student record. One system. Medical college sits on top of the university ERP — no duplication."_

---

### Act 7: Closing (2 min)

- 9 medical DocTypes covering the full MBBS lifecycle
- NMC MSR 2023 compliance built-in (attendance thresholds, faculty norms, CBME)
- Feature-flag gated — zero impact when disabled
- Standalone Frappe app — installs in minutes on any university_app deployment
- Role-based dashboards for Medical Dean and Clinical Coordinator

---

## Quick URL Reference

| Page | URL |
|------|-----|
| Login | http://209.182.233.131:8000/login |
| Medical College Settings | http://209.182.233.131:8000/app/medical-college-settings |
| Medical Dean Dashboard | http://209.182.233.131:8000/app/medical-dean-dashboard |
| Clinical Coordinator Dashboard | http://209.182.233.131:8000/app/clinical-coordinator-dashboard |
| Clinical Postings | http://209.182.233.131:8000/app/mbbs-clinical-posting |
| Case Logs | http://209.182.233.131:8000/app/mbbs-case-log |
| OSCE Assessments | http://209.182.233.131:8000/app/mbbs-osce-assessment |
| Exam Components | http://209.182.233.131:8000/app/mbbs-exam-component |
| NMC Faculty Compliance | http://209.182.233.131:8000/app/nmc-faculty-compliance |
| Curriculum Maps | http://209.182.233.131:8000/app/curriculum-map |
| Teaching Records | http://209.182.233.131:8000/app/teaching-record |
| Dean Dashboard (base) | http://209.182.233.131:8000/app/dean-dashboard |
| Registrar Dashboard | http://209.182.233.131:8000/app/registrar-dashboard |

---

## Troubleshooting

| Issue | Solution |
|-------|---------|
| Dashboard shows "Medical Module Not Configured" | Go to Medical College Settings → check "Enable Medical Module" |
| No data on dashboards | `bench --site walnut execute unity_medical_college.medical_demo_data.seed_demo_data` |
| Charts not rendering | `bench --site walnut clear-cache` then hard-refresh (Ctrl+Shift+R) |
| "No faculty scope" on dean dashboard | Check Role Department Mapping for the logged-in user |
