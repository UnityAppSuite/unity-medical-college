# Unity Medical College

Medical College addon for [University App](https://github.com/UnityAppSuite/university_app) - NMC compliant MBBS management.

## Features

- **Medical College Settings** - Global feature flag and configuration (NMC thresholds, batch size)
- **MBBS Clinical Postings** - Student rotation tracking across clinical departments
- **MBBS Case Logs** - Patient case documentation during clinical postings
- **MBBS OSCE Assessments** - Objective Structured Clinical Examination with station scores
- **MBBS Exam Components** - Theory/Practical/Viva exam results with pass/fail derivation
- **NMC Faculty Compliance** - Regulatory faculty strength tracking per department
- **Curriculum Maps** - Planned teaching sessions per course offering
- **Teaching Records** - Actual delivered sessions linked to curriculum plans
- **Medical Dean Dashboard** - KPI overview for medical college administration
- **Clinical Coordinator Dashboard** - Clinical posting and case log monitoring

## Installation

```bash
cd ~/frappe-bench
bench get-app https://github.com/UnityAppSuite/unity-medical-college
bench --site <site> install-app unity_medical_college
bench --site <site> migrate
```

## Demo Data

Requires university_app with DY Patil demo data (MBBS students, SOM departments) already seeded.

```bash
bench --site <site> execute unity_medical_college.medical_demo_data.execute
```

## Dependencies

- [university_app](https://github.com/UnityAppSuite/university_app) (required)
