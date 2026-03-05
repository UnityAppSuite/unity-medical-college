#!/usr/bin/env python3
"""
Medical College Demo Data Generator
Run: bench --site walnut execute unity_medical_college.medical_demo_data.execute

Builds on top of MBBS students/instructors/departments already created by
dypatil_demo_data.py.  Idempotent — checks frappe.db.exists() before each insert.

Seeded DocTypes:
  - Medical College Settings (enable_medical_module = 1)
  - Curriculum Map        : 30 sessions × course offerings found
  - Teaching Record       : ~80% of Curriculum Map entries
  - MBBS Clinical Posting : students × clinical departments
  - MBBS Case Log         : ~10 per active posting
  - MBBS OSCE Assessment  : 1 per student (5 stations each)
  - MBBS Exam Component   : students × enrolled courses (~15% Fail distribution)
  - NMC Faculty Compliance: one record per department (2–3 depts with shortfall)
"""

import frappe
from frappe.utils import today, add_days, getdate
import random

# ============================================================================
# Constants
# ============================================================================

ACADEMIC_YEAR = "2025-26"

SOM_DEPTS = [
    "Anatomy", "Physiology", "Biochemistry", "Pharmacology", "Pathology",
    "Microbiology", "General Medicine", "General Surgery", "Pediatrics",
    "Obstetrics & Gynecology", "Orthopedics", "Ophthalmology", "ENT",
]
SOM_ABBR = "SOM"
CLINICAL_DEPTS = [
    "General Medicine", "General Surgery", "Pediatrics",
    "Obstetrics & Gynecology", "Orthopedics", "Ophthalmology",
    "ENT", "Pharmacology", "Pathology", "Microbiology",
]

TOPICS_BY_DEPT = {
    "Anatomy": ["Upper Limb", "Lower Limb", "Thorax", "Abdomen", "Head & Neck",
                "Neuroanatomy", "Histology Basics", "Embryology", "Cross Sections", "Osteology"],
    "Physiology": ["Cell Physiology", "Blood & Body Fluids", "Nerve-Muscle", "CVS",
                   "Respiratory", "GIT", "Renal", "Endocrinology", "Reproduction", "CNS"],
    "Biochemistry": ["Carbohydrate Metabolism", "Lipid Metabolism", "Protein Metabolism",
                     "Enzymes", "Vitamins", "Hormones", "Molecular Biology",
                     "Nutrition", "Clinical Biochemistry", "Acid-Base Balance"],
    "Pharmacology": ["General Pharmacology", "ANS Drugs", "CVS Drugs", "CNS Drugs",
                     "Antimicrobials", "Antihypertensives", "Analgesics",
                     "Antidiabetics", "Chemotherapy", "Toxicology"],
    "Pathology": ["Cell Injury", "Inflammation", "Neoplasia", "CVS Pathology",
                  "Respiratory Pathology", "GIT Pathology", "Hepatic Pathology",
                  "Renal Pathology", "Haematology", "Neuropathology"],
    "Microbiology": ["Bacteriology", "Virology", "Mycology", "Parasitology",
                     "Immunology", "Sterilisation", "Hospital Infections",
                     "Antimicrobial Resistance", "Clinical Specimens", "Serology"],
    "General Medicine": ["History Taking", "Respiratory Examination", "CVS Examination",
                         "Abdominal Examination", "CNS Examination", "Case Presentation",
                         "ECG Interpretation", "X-Ray Interpretation",
                         "Common Emergencies", "Bedside Procedures"],
    "General Surgery": ["Wound Management", "Pre-Op Assessment", "Post-Op Care",
                        "Hernias", "GIT Surgery", "Thyroid & Parathyroid",
                        "Breast Surgery", "Vascular Surgery", "Trauma Surgery",
                        "Minor OT Procedures"],
    "Pediatrics": ["Growth & Development", "Neonatal Examination", "Immunisation",
                   "Fever Management", "Respiratory Infections", "GIT in Children",
                   "Nutritional Disorders", "Developmental Milestones",
                   "Common Childhood Diseases", "Pediatric Emergencies"],
    "Obstetrics & Gynecology": ["Antenatal Care", "Normal Labour", "Complicated Labour",
                                "Postnatal Care", "Contraception", "Gynaecological Examination",
                                "Menstrual Disorders", "Gynaecological Cancers",
                                "Infertility", "Obstetric Emergencies"],
    "Orthopedics": ["Fracture Basics", "Upper Limb Fractures", "Lower Limb Fractures",
                    "Spine Disorders", "Arthritis", "Bone Tumours",
                    "Joint Replacement", "Sports Injuries", "Paediatric Ortho",
                    "Plaster Techniques"],
    "Ophthalmology": ["Ocular Examination", "Refractive Errors", "Glaucoma",
                      "Cataract", "Retinal Disorders", "Corneal Diseases",
                      "Uveal Tract", "Squint", "Ocular Emergencies", "Low Vision"],
    "ENT": ["ENT Examination", "Ear Infections", "Hearing Loss", "Nasal Disorders",
            "Sinusitis", "Throat Infections", "Laryngeal Disorders",
            "Head & Neck Masses", "Vertigo", "ENT Emergencies"],
}

COMPLAINTS = [
    "Fever with chills", "Shortness of breath", "Chest pain", "Abdominal pain",
    "Headache", "Vomiting and nausea", "Diarrhoea", "Cough for 3 weeks",
    "Swelling of legs", "Difficulty swallowing", "Blurred vision", "Back pain",
    "Joint pain", "Skin rash", "Weakness of limbs",
]

DIAGNOSES = {
    "General Medicine": ["Type 2 Diabetes Mellitus", "Hypertension", "Pneumonia",
                         "Acute MI", "Stroke", "Anaemia", "Typhoid Fever"],
    "General Surgery": ["Appendicitis", "Inguinal Hernia", "Cholecystitis",
                        "Intestinal Obstruction", "Trauma", "Varicose Veins"],
    "Pediatrics": ["Bronchopneumonia", "Acute Gastroenteritis", "Febrile Seizure",
                   "Nutritional Anaemia", "Dengue Fever"],
    "Obstetrics & Gynecology": ["Gestational Diabetes", "Pre-eclampsia",
                                "Uterine Fibroid", "PCOS", "Ectopic Pregnancy"],
    "default": ["Pyrexia of Unknown Origin", "Viral Fever", "Cellulitis",
                "Urinary Tract Infection", "Hypertensive Crisis"],
}

NMC_NORMS = {
    "Anatomy": {"professors": 2, "assoc": 2, "asst": 3},
    "Physiology": {"professors": 2, "assoc": 2, "asst": 3},
    "Biochemistry": {"professors": 2, "assoc": 2, "asst": 3},
    "Pharmacology": {"professors": 2, "assoc": 2, "asst": 2},
    "Pathology": {"professors": 2, "assoc": 2, "asst": 3},
    "Microbiology": {"professors": 2, "assoc": 2, "asst": 2},
    "General Medicine": {"professors": 3, "assoc": 3, "asst": 4},
    "General Surgery": {"professors": 3, "assoc": 3, "asst": 4},
    "Pediatrics": {"professors": 2, "assoc": 2, "asst": 3},
    "Obstetrics & Gynecology": {"professors": 2, "assoc": 2, "asst": 3},
    "Orthopedics": {"professors": 2, "assoc": 2, "asst": 3},
    "Ophthalmology": {"professors": 1, "assoc": 1, "asst": 2},
    "ENT": {"professors": 1, "assoc": 1, "asst": 2},
}

# Depts that will show shortfall for demo impact
SHORTFALL_DEPTS = {"General Surgery", "Orthopedics", "Ophthalmology"}


# ============================================================================
# Helpers
# ============================================================================

def get_full_dept_name(dept_name):
    full = f"{dept_name} - {SOM_ABBR}"
    return full if frappe.db.exists("Department", full) else dept_name


def get_mbbs_students():
    """Return list of Student names enrolled in the MBBS program."""
    students = frappe.db.sql(
        """
        SELECT DISTINCT pe.student
        FROM `tabProgram Enrollment` pe
        INNER JOIN `tabStudent` s ON s.name = pe.student
        WHERE pe.program LIKE '%MBBS%'
        LIMIT 200
        """,
        as_dict=True,
    )
    if not students:
        # Fallback: any student whose name starts with DYP25SOM
        students = frappe.get_all(
            "Student",
            filters={"name": ["like", "DYP25SOM%"]},
            fields=["name as student"],
        )
    return [r.student for r in students]


def get_instructors_for_dept(dept_name):
    full = get_full_dept_name(dept_name)
    rows = frappe.get_all(
        "Instructor",
        filters={"department": full},
        fields=["name"],
        limit=5,
    )
    return [r.name for r in rows]


def get_course_offerings():
    """Return course offerings linked to MBBS-like courses."""
    rows = frappe.get_all(
        "Course Offering",
        fields=["name", "course"],
        limit=50,
    )
    return rows


# ============================================================================
# Step functions
# ============================================================================

def enable_medical_settings():
    print("\n⚙️  Enabling Medical College Settings...")
    doc = frappe.get_single("Medical College Settings")
    doc.enable_medical_module = 1
    doc.institution_name = "D.Y. Patil University School of Medicine"
    doc.regulatory_body = "NMC"
    doc.max_batch_size = 150
    doc.theory_attendance_threshold = 75
    doc.clinical_attendance_threshold = 75
    doc.enable_curriculum_map = 1
    doc.enable_case_logs = 1
    doc.enable_osce = 1
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    print("  ✓ Medical module enabled")


def create_curriculum_maps():
    """30 Curriculum Map entries per course offering (up to 15 offerings)."""
    print("\n📚 Creating Curriculum Maps...")
    offerings = get_course_offerings()[:15]
    count = 0

    teaching_methods = ["Lecture", "Tutorial", "Practical", "Clinical", "Bedside Teaching"]

    for offering in offerings:
        dept_topics = TOPICS_BY_DEPT.get("General Medicine", ["Topic"] * 10)
        # Derive dept from course name for topic variety
        for dept, topics in TOPICS_BY_DEPT.items():
            if dept.lower() in (offering.course or "").lower():
                dept_topics = topics
                break

        for unit_no in range(1, 31):
            topic = dept_topics[(unit_no - 1) % len(dept_topics)]

            existing = frappe.db.exists(
                "Curriculum Map",
                {"course_offering": offering.name, "unit_number": unit_no},
            )
            if existing:
                count += 1
                continue

            cm = frappe.get_doc({
                "doctype": "Curriculum Map",
                "course_offering": offering.name,
                "unit_number": unit_no,
                "unit_title": f"Unit {unit_no}",
                "topic": topic,
                "learning_outcome": f"Students will be able to explain {topic.lower()}",
                "teaching_method": teaching_methods[unit_no % len(teaching_methods)],
                "planned_week": ((unit_no - 1) // 2) + 1,
                "estimated_hours": 1.0 + (unit_no % 3) * 0.5,
            })
            cm.insert(ignore_permissions=True)
            count += 1

    frappe.db.commit()
    print(f"  ✓ {count} Curriculum Map entries")
    return count


def create_teaching_records():
    """Create Teaching Records for ~80% of Curriculum Map entries."""
    print("\n📝 Creating Teaching Records...")
    cms = frappe.get_all(
        "Curriculum Map",
        fields=["name", "course_offering", "topic", "teaching_method", "unit_number"],
        limit=500,
    )

    # Thin to 80%
    random.shuffle(cms)
    cms_to_cover = cms[: int(len(cms) * 0.8)]

    count = 0
    base_date = getdate("2025-08-01")

    for cm in cms_to_cover:
        existing = frappe.db.exists("Teaching Record", {"curriculum_map": cm.name})
        if existing:
            count += 1
            continue

        # Find an instructor for this course offering
        instructors = frappe.get_all(
            "Instructor",
            fields=["name"],
            limit=1,
        )
        instructor = instructors[0].name if instructors else None
        if not instructor:
            continue

        session_date = add_days(base_date, (cm.unit_number - 1) * 3)

        # session_type options: Lecture, Tutorial, Practical, Clinical, Bedside Teaching
        # teaching_method options: Lecture, Tutorial, Practical, Clinical Demo, ICT
        _session_map = {
            "Lecture": "Lecture", "Tutorial": "Tutorial", "Practical": "Practical",
            "Clinical": "Clinical", "Bedside Teaching": "Bedside Teaching",
            "Clinical Demo": "Clinical", "ICT": "Lecture",
        }
        _method_map = {
            "Lecture": "Lecture", "Tutorial": "Tutorial", "Practical": "Practical",
            "Clinical Demo": "Clinical Demo", "ICT": "ICT",
            "Clinical": "Clinical Demo", "Bedside Teaching": "Clinical Demo",
        }
        raw_type = cm.teaching_method or "Lecture"
        session_type = _session_map.get(raw_type, "Lecture")
        teaching_method = _method_map.get(raw_type, "Lecture")

        tr = frappe.get_doc({
            "doctype": "Teaching Record",
            "instructor": instructor,
            "course_offering": cm.course_offering,
            "session_date": session_date,
            "session_type": session_type,
            "curriculum_map": cm.name,
            "topic_covered": cm.topic,
            "teaching_method": teaching_method,
            "students_present": random.randint(60, 140),
            "duration_hours": 1.0,
            "remarks": "Session completed as per curriculum plan.",
        })
        tr.insert(ignore_permissions=True)
        count += 1

    frappe.db.commit()
    print(f"  ✓ {count} Teaching Records")
    return count


def create_clinical_postings(students):
    """Create 1 posting per student per clinical department (Phase 3 rotation)."""
    print("\n🏥 Creating MBBS Clinical Postings...")
    count = 0
    ay_name = ACADEMIC_YEAR if frappe.db.exists("Academic Year", ACADEMIC_YEAR) else None

    # Get any available instructors as supervisors
    supervisors = frappe.get_all("Instructor", fields=["name"], limit=20)
    supervisor_names = [s.name for s in supervisors]

    posting_start = getdate("2025-08-01")

    created_postings = {}  # student → [posting_name, ...]

    for student in students:
        for i, dept_name in enumerate(CLINICAL_DEPTS):
            full_dept = get_full_dept_name(dept_name)
            if not frappe.db.exists("Department", full_dept):
                full_dept = dept_name

            existing = frappe.db.exists(
                "MBBS Clinical Posting",
                {"student": student, "department": full_dept},
            )
            if existing:
                if student not in created_postings:
                    created_postings[student] = []
                created_postings[student].append(existing)
                count += 1
                continue

            start = add_days(posting_start, i * 14)
            end = add_days(start, 13)
            theory_pct = round(random.uniform(55, 98), 1)
            clinical_pct = round(random.uniform(60, 99), 1)
            supervisor = random.choice(supervisor_names) if supervisor_names else None

            posting = frappe.get_doc({
                "doctype": "MBBS Clinical Posting",
                "student": student,
                "academic_year": ay_name,
                "department": full_dept,
                "posting_type": "Compulsory",
                "start_date": str(start),
                "end_date": str(end),
                "supervisor": supervisor,
                "attendance_theory_pct": theory_pct,
                "attendance_clinical_pct": clinical_pct,
                "status": "Completed",
            })
            posting.insert(ignore_permissions=True)
            if student not in created_postings:
                created_postings[student] = []
            created_postings[student].append(posting.name)
            count += 1

    frappe.db.commit()
    print(f"  ✓ {count} Clinical Postings")
    return created_postings


def create_case_logs(created_postings):
    """Create ~10 case logs per posting."""
    print("\n📋 Creating MBBS Case Logs...")
    count = 0
    case_types = ["Observed", "Assisted", "Independent"]

    for student, posting_names in created_postings.items():
        for posting_name in posting_names:
            # Get posting dept for contextual diagnosis
            posting = frappe.db.get_value(
                "MBBS Clinical Posting", posting_name, ["department", "start_date"], as_dict=True
            )
            if not posting:
                continue

            dept_key = "default"
            for d in DIAGNOSES:
                if d.lower() in (posting.department or "").lower():
                    dept_key = d
                    break
            diag_list = DIAGNOSES[dept_key]
            base_date = getdate(posting.start_date or "2025-08-01")

            for j in range(10):
                existing = frappe.db.count(
                    "MBBS Case Log",
                    filters={"clinical_posting": posting_name},
                )
                if existing >= 10:
                    count += existing
                    break

                case_date = add_days(base_date, j)
                cl = frappe.get_doc({
                    "doctype": "MBBS Case Log",
                    "student": student,
                    "clinical_posting": posting_name,
                    "case_date": str(case_date),
                    "patient_age": random.randint(18, 75),
                    "patient_gender": random.choice(["Male", "Female"]),
                    "presenting_complaint": random.choice(COMPLAINTS),
                    "diagnosis": random.choice(diag_list),
                    "case_type": random.choice(case_types),
                    "supervisor_verified": random.choice([0, 1]),
                    "submission_date": str(add_days(case_date, 1)),
                })
                cl.insert(ignore_permissions=True)
                count += 1

    frappe.db.commit()
    print(f"  ✓ {count} Case Logs")
    return count


def create_osce_assessments(students):
    """Create 1 OSCE assessment per student (5 stations)."""
    print("\n🩺 Creating MBBS OSCE Assessments...")
    count = 0
    station_types = ["History", "Examination", "Procedure", "Communication", "History"]

    # Resolve academic term
    at_name = frappe.db.get_value("Academic Term", {"academic_year": ACADEMIC_YEAR}, "name")
    gm_dept = get_full_dept_name("General Medicine")
    exam_date = "2026-01-15"

    for student in students:
        existing = frappe.db.exists("MBBS OSCE Assessment", {"student": student})
        if existing:
            count += 1
            continue

        # 20% fail rate
        fail = random.random() < 0.20
        stations = []
        total = 0.0
        for sno in range(1, 6):
            max_m = 20.0
            obtained = round(random.uniform(8, max_m) if not fail else random.uniform(4, 9), 1)
            total += obtained
            stations.append({
                "doctype": "MBBS OSCE Station Score",
                "station_no": sno,
                "station_type": station_types[sno - 1],
                "marks_obtained": obtained,
                "max_marks": max_m,
                "examiner": "Examiner",
            })

        osce = frappe.get_doc({
            "doctype": "MBBS OSCE Assessment",
            "student": student,
            "exam_date": exam_date,
            "academic_term": at_name,
            "department": gm_dept if frappe.db.exists("Department", gm_dept) else None,
            "station_count": 5,
            "total_score": round(total, 1),
            "pass_fail": "Fail" if fail else "Pass",
            "station_scores": stations,
        })
        osce.insert(ignore_permissions=True)
        count += 1

    frappe.db.commit()
    print(f"  ✓ {count} OSCE Assessments")
    return count


def create_exam_components(students):
    """Create exam component records (theory/practical/viva) per student."""
    print("\n📊 Creating MBBS Exam Components...")
    count = 0

    # Get up to 5 course enrollments per student
    for student in students:
        enrollments = frappe.get_all(
            "Course Enrollment",
            filters={"student": student},
            fields=["name"],
            limit=5,
        )

        for enr in enrollments:
            existing = frappe.db.exists(
                "MBBS Exam Component", {"course_enrollment": enr.name}
            )
            if existing:
                count += 1
                continue

            # ~15% overall fail rate
            fail_overall = random.random() < 0.15
            if fail_overall:
                theory_s = random.choice(["Fail", "Pass"])
                prac_s = "Fail" if theory_s == "Pass" else "Pass"
                viva_s = "Pass"
                overall = "Fail"
            else:
                theory_s = prac_s = viva_s = "Pass"
                overall = "Pass"

            ec = frappe.get_doc({
                "doctype": "MBBS Exam Component",
                "course_enrollment": enr.name,
                "theory_ia": round(random.uniform(20, 30), 1),
                "theory_university": round(random.uniform(40, 60), 1) if theory_s == "Pass" else round(random.uniform(20, 35), 1),
                "practical_ia": round(random.uniform(15, 25), 1),
                "practical_university": round(random.uniform(30, 50), 1) if prac_s == "Pass" else round(random.uniform(15, 28), 1),
                "viva_marks": round(random.uniform(15, 25), 1) if viva_s == "Pass" else round(random.uniform(8, 14), 1),
                "theory_status": theory_s,
                "practical_status": prac_s,
                "viva_status": viva_s,
                "overall_result": overall,
            })
            ec.insert(ignore_permissions=True)
            count += 1

    frappe.db.commit()
    print(f"  ✓ {count} Exam Components")
    return count


def create_nmc_faculty_compliance():
    """Create NMC Faculty Compliance records for all SOM departments."""
    print("\n🏛️  Creating NMC Faculty Compliance records...")
    count = 0
    ay_name = ACADEMIC_YEAR if frappe.db.exists("Academic Year", ACADEMIC_YEAR) else None

    for dept_name in SOM_DEPTS:
        full_dept = get_full_dept_name(dept_name)
        if not frappe.db.exists("Department", full_dept):
            continue

        existing = frappe.db.exists(
            "NMC Faculty Compliance",
            {"department": full_dept, "academic_year": ay_name},
        )
        if existing:
            count += 1
            continue

        norms = NMC_NORMS.get(dept_name, {"professors": 2, "assoc": 2, "asst": 3})
        shortfall = dept_name in SHORTFALL_DEPTS

        if shortfall:
            # Simulate 1-professor shortfall for demo impact
            actual_p = max(0, norms["professors"] - 1)
            actual_a = norms["assoc"]
            actual_as = norms["asst"]
            note = f"Professor shortfall in {dept_name}. Recruitment in progress."
        else:
            actual_p = norms["professors"]
            actual_a = norms["assoc"]
            actual_as = norms["asst"]
            note = ""

        compliant = int(
            actual_p >= norms["professors"]
            and actual_a >= norms["assoc"]
            and actual_as >= norms["asst"]
        )

        nfc = frappe.get_doc({
            "doctype": "NMC Faculty Compliance",
            "department": full_dept,
            "academic_year": ay_name,
            "required_professors": norms["professors"],
            "required_assoc_prof": norms["assoc"],
            "required_asst_prof": norms["asst"],
            "actual_professors": actual_p,
            "actual_assoc_prof": actual_a,
            "actual_asst_prof": actual_as,
            "compliant": compliant,
            "shortfall_note": note,
        })
        nfc.insert(ignore_permissions=True)
        count += 1

    frappe.db.commit()
    print(f"  ✓ {count} NMC Faculty Compliance records")
    return count


# ============================================================================
# Main
# ============================================================================

def execute():
    print("=" * 60)
    print("  Medical College Demo Data Generator")
    print("=" * 60)

    import time
    random.seed(42)  # Reproducible data

    # Step 0: Enable settings
    enable_medical_settings()

    # Step 1: Get MBBS students
    students = get_mbbs_students()
    print(f"\n  Found {len(students)} MBBS students to seed against.")
    if not students:
        print("  ⚠ No MBBS students found. Run dypatil_demo_data first.")
        print("  bench --site walnut execute university_app.dypatil_demo_data.execute")  # prerequisite from university_app
        return

    # Step 2: Curriculum maps
    create_curriculum_maps()

    # Step 3: Teaching records
    create_teaching_records()

    # Step 4: Clinical postings (returns dict student → [posting names])
    created_postings = create_clinical_postings(students)

    # Step 5: Case logs
    create_case_logs(created_postings)

    # Step 6: OSCE assessments
    create_osce_assessments(students)

    # Step 7: Exam components
    create_exam_components(students)

    # Step 8: NMC faculty compliance
    create_nmc_faculty_compliance()

    frappe.db.commit()

    print("\n" + "=" * 60)
    print("  Medical demo data seeded successfully!")
    print("  Visit: /app/medical-dean-dashboard")
    print("  Visit: /app/clinical-coordinator-dashboard")
    print("=" * 60)
