# Unity Medical College - Demo Walkthrough

**Date**: March 2026
**Duration**: ~30 minutes
**Audience**: University registrars, medical college deans, academic administrators

> **Replace `YOUR_SITE_URL` below with your actual bench URL**
> (e.g., `http://209.182.233.131:8000` or `http://localhost:8000`)

---

## Pre-Demo Setup (Run Once)

```bash
# 1. Install the medical addon (from university_app repo)
cd ~/frappe-bench
bench get-app /path/to/unity-medical-college   # or GitHub URL
bench --site <site> install-app unity_medical_college
bench --site <site> migrate

# 2. Seed demo data (requires DY Patil demo data already loaded)
bench --site <site> execute unity_medical_college.medical_demo_data.execute

# 3. Restart bench
bench restart   # or: bench start (dev mode)
```

---

## Demo Credentials

| Role | Email | Password | Dashboard |
|------|-------|----------|-----------|
| **Registrar** | registrar@dypatil.edu | DyPatil@2025Demo | `/app/registrar-dashboard` |
| **Dean** | dean@dypatil.edu | DyPatil@2025Demo | `/app/dean-dashboard` |
| **Admin** | Administrator | 12345 | Full access |

---

## Walkthrough Script

### Act 1: Introduction (2 min)

**Talking points:**
- Unity Medical College is a standalone addon that adds NMC-compliant medical college management
- It installs alongside the core University App and adds medical-specific features
- Feature-flag gated: can be enabled/disabled without affecting the base system

### Act 2: Enable the Medical Module (3 min)

1. **Login** as Administrator
   - URL: `YOUR_SITE_URL/login`

2. **Navigate to Medical College Settings**
   - URL: `YOUR_SITE_URL/app/medical-college-settings`
   - Or: Search bar > type "Medical College Settings"

3. **Show the settings panel:**
   - **Enable Medical Module** checkbox (should already be checked if demo data was seeded)
   - **Institution Name**: D.Y. Patil University School of Medicine
   - **Regulatory Body**: NMC (National Medical Commission)
   - **Attendance Thresholds**: Theory 75%, Clinical 75% (NMC MSR 2023 norms)
   - **Feature Flags**: Curriculum Map, Case Logs, OSCE all enabled

4. **Key message**: _"This is a single toggle. When disabled, all medical features gracefully hide. When enabled, the entire medical workflow lights up."_

### Act 3: Medical Dean Dashboard (10 min)

1. **Navigate to the Medical Dean Dashboard**
   - URL: `YOUR_SITE_URL/app/medical-dean-dashboard`

2. **KPI Cards (top row)** — walk through each:

   | KPI | What it shows | Demo value | NMC reference |
   |-----|--------------|------------|---------------|
   | **Student Eligibility Rate** | % of students meeting NMC attendance thresholds | ~85-95% | MSR 2023: Theory >=75%, Clinical >=80% |
   | **Attendance Defaulters** | Students below NMC threshold | Red if >0 | Students at risk of being barred from exams |
   | **Faculty NMC Compliance** | % of departments meeting faculty strength norms | ~77% (10/13) | MSR 2023 faculty-student ratios |
   | **Theory Exam Pass %** | Theory exam pass rate | ~85% | NMC pass mark: 50% |
   | **Practical Pass %** | Practical exam pass rate | ~85% | NMC pass mark: 50% |
   | **Curriculum Coverage** | Sessions delivered vs. planned (CBME) | ~80% | CBME curriculum completion tracking |

3. **Charts** — walk through:
   - **Batch Phase Distribution**: Bar chart showing students across MBBS phases (Phase 1/2/3A/3B/Internship)
   - **Attendance Defaulters by Department**: Which departments have the most at-risk students
   - **Exam Component Pass Rates**: Theory vs Practical vs Viva vs Overall comparison
   - **CBME Case Log Completion**: Donut chart showing submitted vs pending case logs

4. **Filters**: Show how Academic Year / Term filters dynamically update all KPIs and charts

5. **Key message**: _"The Medical Dean gets a single-screen view of NMC compliance, exam performance, and curriculum delivery — everything needed for accreditation readiness."_

### Act 4: Clinical Coordinator Dashboard (5 min)

1. **Navigate to Clinical Coordinator Dashboard**
   - URL: `YOUR_SITE_URL/app/clinical-coordinator-dashboard`

2. **Walk through the clinical operations view:**
   - Active clinical postings by department
   - Case log submission tracking
   - OSCE assessment results
   - Student rotation schedules

3. **Key message**: _"The Clinical Coordinator manages day-to-day clinical training — rotations, case logs, and assessments — all tracked in real-time."_

### Act 5: Browse Medical Records (5 min)

Show the underlying data that powers the dashboards:

1. **Clinical Postings List**
   - URL: `YOUR_SITE_URL/app/mbbs-clinical-posting`
   - Show: Student rotations across departments, attendance percentages, status
   - Click into one posting to show detail view

2. **Case Logs**
   - URL: `YOUR_SITE_URL/app/mbbs-case-log`
   - Show: Patient cases documented during rotations
   - Fields: complaint, diagnosis, case type (Observed/Assisted/Independent), supervisor verified

3. **OSCE Assessments**
   - URL: `YOUR_SITE_URL/app/mbbs-osce-assessment`
   - Show: Station-based clinical exam scores (5 stations x 20 marks)
   - Click into one to see station scores breakdown

4. **Exam Components**
   - URL: `YOUR_SITE_URL/app/mbbs-exam-component`
   - Show: Theory/Practical/Viva independent pass/fail tracking
   - ~15% fail rate in demo data for realistic distribution

5. **NMC Faculty Compliance**
   - URL: `YOUR_SITE_URL/app/nmc-faculty-compliance`
   - Show: Required vs Actual faculty strength per department
   - 3 departments with shortfall (General Surgery, Orthopedics, Ophthalmology)
   - Compliant flag auto-derived

6. **Curriculum Maps**
   - URL: `YOUR_SITE_URL/app/curriculum-map`
   - Show: Planned teaching sessions per course offering
   - 30 units per course with topics, learning outcomes, teaching methods

7. **Teaching Records**
   - URL: `YOUR_SITE_URL/app/teaching-record`
   - Show: Actual sessions delivered, linked to curriculum plan
   - ~80% coverage rate (planned vs delivered)

### Act 6: Integration with University App (3 min)

1. **Show the Dean Dashboard** (existing university_app)
   - URL: `YOUR_SITE_URL/app/dean-dashboard`
   - Point out how the base university features (enrollment, GPA, promotions) continue to work alongside medical features

2. **Show a Student Record**
   - URL: `YOUR_SITE_URL/app/student`
   - Filter by MBBS students
   - Show how the same student appears in both university_app (enrollment, GPA) and medical module (postings, case logs, OSCE)

3. **Key message**: _"Medical college management is seamlessly integrated with the core university ERP. One student record, one system."_

### Act 7: Closing (2 min)

**Summary talking points:**
- 9 medical DocTypes covering the full MBBS lifecycle
- NMC MSR 2023 compliance built-in (attendance thresholds, faculty norms, CBME tracking)
- Feature-flag gated — enable/disable without affecting the base system
- Standalone Frappe app — installs in minutes, works with any university_app deployment
- Role-based dashboards for Medical Dean and Clinical Coordinator
- All data is real-time, filterable, and exportable

---

## Demo Data Summary

| DocType | Approximate Count | Notes |
|---------|-------------------|-------|
| MBBS Students | ~200+ | Enrolled in MBBS program |
| Clinical Postings | ~2,000+ | 200 students x 10 clinical departments |
| Case Logs | ~20,000+ | ~10 per posting |
| OSCE Assessments | ~200 | 1 per student, 5 stations each |
| Exam Components | ~1,000+ | ~5 per student |
| NMC Faculty Compliance | 13 | 1 per SOM department (3 with shortfall) |
| Curriculum Maps | ~450 | 30 per course offering |
| Teaching Records | ~360 | ~80% of curriculum maps |

---

## Quick URL Reference

| Page | URL |
|------|-----|
| Login | `YOUR_SITE_URL/login` |
| Medical College Settings | `YOUR_SITE_URL/app/medical-college-settings` |
| Medical Dean Dashboard | `YOUR_SITE_URL/app/medical-dean-dashboard` |
| Clinical Coordinator Dashboard | `YOUR_SITE_URL/app/clinical-coordinator-dashboard` |
| Clinical Postings | `YOUR_SITE_URL/app/mbbs-clinical-posting` |
| Case Logs | `YOUR_SITE_URL/app/mbbs-case-log` |
| OSCE Assessments | `YOUR_SITE_URL/app/mbbs-osce-assessment` |
| Exam Components | `YOUR_SITE_URL/app/mbbs-exam-component` |
| NMC Faculty Compliance | `YOUR_SITE_URL/app/nmc-faculty-compliance` |
| Curriculum Maps | `YOUR_SITE_URL/app/curriculum-map` |
| Teaching Records | `YOUR_SITE_URL/app/teaching-record` |
| Dean Dashboard (base) | `YOUR_SITE_URL/app/dean-dashboard` |
| Registrar Dashboard | `YOUR_SITE_URL/app/registrar-dashboard` |

---

## Troubleshooting

| Issue | Solution |
|-------|---------|
| Dashboard shows "Medical Module Not Configured" | Go to Medical College Settings and check "Enable Medical Module" |
| No data on dashboards | Run: `bench --site <site> execute unity_medical_college.medical_demo_data.execute` |
| "No MBBS students found" during data seeding | Run DY Patil demo data first: `bench --site <site> execute university_app.dypatil_demo_data.execute` |
| Charts not rendering | Clear cache: `bench --site <site> clear-cache` then hard-refresh browser (Ctrl+Shift+R) |
