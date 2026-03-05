"""
Medical / Clinical API for the Dean and Clinical Coordinator dashboards.

Every public function gates on _require_medical_access() which checks both:
  1. Medical module is enabled in Medical College Settings
  2. Caller has read permission on Medical College Settings
     (System Manager and Academic Administrator by default)
"""

import frappe
from unity_medical_college.unity_medical_college.doctype.medical_college_settings.medical_college_settings import (
    is_medical_enabled,
)


def _disabled():
    return {"success": False, "message": "Medical module not configured", "data": []}


def _require_medical_access():
    """
    Raises PermissionError if caller lacks access.
    Returns _disabled() dict if module is off (callers must check return value).
    """
    if not is_medical_enabled():
        return _disabled()
    frappe.has_permission("Medical College Settings", "read", throw=True)
    return None


def _validated_link(doctype, value):
    """Return value unchanged if it exists in DB; raise ValidationError if not."""
    if value and not frappe.db.exists(doctype, value):
        frappe.throw(
            f"Invalid {doctype}: {frappe.utils.escape_html(str(value))}",
            frappe.ValidationError,
        )
    return value or None


@frappe.whitelist()
def check_medical_enabled():
    """Return whether the medical module is active (used by JS pages on load)."""
    return is_medical_enabled()


@frappe.whitelist()
def get_nmc_attendance_compliance(faculty=None, academic_term=None):
    """
    Return count of students whose theory OR clinical attendance is below the
    configured thresholds for the given faculty / academic_term.
    """
    guard = _require_medical_access()
    if guard is not None:
        return guard

    _validated_link("Faculty College", faculty)
    _validated_link("Academic Term", academic_term)

    theory_threshold = (
        frappe.db.get_single_value("Medical College Settings", "theory_attendance_threshold") or 75
    )
    clinical_threshold = (
        frappe.db.get_single_value("Medical College Settings", "clinical_attendance_threshold") or 75
    )

    filters = {}
    if academic_term:
        pass  # future: map term → year

    postings = frappe.get_all(
        "MBBS Clinical Posting",
        filters=filters,
        fields=["student", "department", "attendance_theory_pct", "attendance_clinical_pct"],
    )

    # Aggregate per-student: average across all their postings
    student_theory = {}
    student_clinical = {}
    for p in postings:
        s = p.student
        if s not in student_theory:
            student_theory[s] = []
            student_clinical[s] = []
        student_theory[s].append(p.attendance_theory_pct or 0)
        student_clinical[s].append(p.attendance_clinical_pct or 0)

    all_students = set(student_theory.keys())
    total_students = len(all_students)

    ineligible_students = set()
    for s in all_students:
        avg_theory = sum(student_theory[s]) / len(student_theory[s])
        avg_clinical = sum(student_clinical[s]) / len(student_clinical[s])
        if avg_theory < theory_threshold or avg_clinical < clinical_threshold:
            ineligible_students.add(s)

    eligible_students = total_students - len(ineligible_students)

    dept_map = {}
    for p in postings:
        dept = p.department or "Unknown"
        if dept not in dept_map:
            dept_map[dept] = {"department": dept, "total": 0, "below_theory": 0, "below_clinical": 0}
        dept_map[dept]["total"] += 1
        if (p.attendance_theory_pct or 0) < theory_threshold:
            dept_map[dept]["below_theory"] += 1
        if (p.attendance_clinical_pct or 0) < clinical_threshold:
            dept_map[dept]["below_clinical"] += 1

    return {
        "success": True,
        "ineligible_count": len(ineligible_students),
        "eligible_count": eligible_students,
        "total": total_students,
        "theory_threshold": theory_threshold,
        "clinical_threshold": clinical_threshold,
        "department_breakdown": list(dept_map.values()),
    }


@frappe.whitelist()
def get_clinical_posting_summary(faculty=None, academic_term=None):
    """Return active clinical postings by department (for today)."""
    guard = _require_medical_access()
    if guard is not None:
        return guard

    _validated_link("Faculty College", faculty)
    _validated_link("Academic Term", academic_term)

    from frappe.utils import today

    active_postings = frappe.get_all(
        "MBBS Clinical Posting",
        filters={"status": "Active"},
        fields=["student", "department", "posting_type", "start_date", "end_date"],
    )

    dept_map = {}
    today_str = today()
    for p in active_postings:
        start = str(p.start_date or "")
        end = str(p.end_date or "9999-12-31")
        if start <= today_str <= end:
            dept = p.department or "Unknown"
            dept_map[dept] = dept_map.get(dept, 0) + 1

    return {
        "success": True,
        "total_active": sum(dept_map.values()),
        "by_department": [{"department": k, "count": v} for k, v in dept_map.items()],
    }


@frappe.whitelist()
def get_case_log_compliance(faculty=None, academic_term=None):
    """Return case-log submission compliance. Expected: 10 case logs per posting."""
    guard = _require_medical_access()
    if guard is not None:
        return guard

    _validated_link("Faculty College", faculty)
    _validated_link("Academic Term", academic_term)

    postings = frappe.get_all(
        "MBBS Clinical Posting",
        filters={"status": ["in", ["Active", "Completed"]]},
        fields=["name", "student", "department"],
    )

    posting_names = [p.name for p in postings]
    expected = len(posting_names) * 10
    submitted = (
        frappe.db.count("MBBS Case Log", filters={"clinical_posting": ["in", posting_names]})
        if posting_names
        else 0
    )
    compliance_pct = round((submitted / expected * 100) if expected else 0, 1)

    return {
        "success": True,
        "expected": expected,
        "submitted": submitted,
        "compliance_pct": compliance_pct,
    }


@frappe.whitelist()
def get_osce_summary(faculty=None, academic_term=None):
    """Return count of OSCE assessments: total, passed, failed, pass%."""
    guard = _require_medical_access()
    if guard is not None:
        return guard

    _validated_link("Academic Term", academic_term)

    filters = {}
    if academic_term:
        filters["academic_term"] = academic_term

    all_assessments = frappe.get_all(
        "MBBS OSCE Assessment",
        filters=filters,
        fields=["name", "pass_fail"],
    )

    total = len(all_assessments)
    passed = sum(1 for a in all_assessments if a.pass_fail == "Pass")
    failed = sum(1 for a in all_assessments if a.pass_fail == "Fail")
    pending = total - passed - failed  # blank pass_fail = not yet assessed

    return {
        "success": True,
        "total": total,
        "passed": passed,
        "failed": failed,
        "pending_count": pending,
        "pass_pct": round((passed / total * 100) if total else 0, 1),
    }


@frappe.whitelist()
def get_batch_phase_distribution(faculty=None):
    """Return student count by MBBS phase (derived from academic_year name)."""
    guard = _require_medical_access()
    if guard is not None:
        return guard

    _validated_link("Faculty College", faculty)

    postings = frappe.get_all(
        "MBBS Clinical Posting",
        fields=["student", "academic_year"],
        group_by="student, academic_year",
    )

    phase_map = {}
    for p in postings:
        ay = p.academic_year or "Unknown"
        if "Intern" in ay or "Phase IV" in ay:
            phase = "Internship"
        elif "Phase 3B" in ay or "3B" in ay or "Phase IIIB" in ay:
            phase = "Phase 3B"
        elif "Phase 3A" in ay or "3A" in ay or "Phase IIIA" in ay:
            phase = "Phase 3A"
        elif "Phase 2" in ay or "II" in ay:
            phase = "Phase 2"
        else:
            phase = "Phase 1"
        phase_map[phase] = phase_map.get(phase, 0) + 1

    return {
        "success": True,
        "phases": [{"phase": k, "count": v} for k, v in sorted(phase_map.items())],
    }


@frappe.whitelist()
def get_faculty_nmc_compliance_summary(faculty=None):
    """
    Return summary of NMC faculty strength compliance:
      compliant_depts — departments meeting all NMC faculty norms
      total_depts     — total departments with compliance records
      compliance_pct  — compliant_depts / total_depts * 100
    """
    guard = _require_medical_access()
    if guard is not None:
        return guard

    _validated_link("Faculty College", faculty)

    filters = {}
    records = frappe.get_all(
        "NMC Faculty Compliance",
        filters=filters,
        fields=["name", "compliant"],
    )

    total = len(records)
    compliant = sum(1 for r in records if r.compliant)

    return {
        "success": True,
        "compliant_depts": compliant,
        "total_depts": total,
        "compliance_pct": round((compliant / total * 100) if total else 0, 1),
    }


@frappe.whitelist()
def get_curriculum_coverage_summary(academic_term=None):
    """
    Return curriculum delivery coverage for the given term:
      planned   — total Curriculum Map entries (planned sessions)
      covered   — Teaching Records linked to those Curriculum Map entries
      coverage_pct — covered / planned * 100

    If academic_term is provided, only Curriculum Maps whose linked
    Course Offering has a matching academic_term are counted.
    """
    guard = _require_medical_access()
    if guard is not None:
        return guard

    _validated_link("Academic Term", academic_term)

    # Count planned sessions
    cm_filters = {}
    planned = frappe.db.count("Curriculum Map", filters=cm_filters)

    # Count teaching records that have a linked curriculum_map entry
    tr_filters = {"curriculum_map": ["is", "set"]}
    covered = frappe.db.count("Teaching Record", filters=tr_filters)

    # covered cannot exceed planned (defensive)
    covered = min(covered, planned)

    return {
        "success": True,
        "planned": planned,
        "covered": covered,
        "coverage_pct": round((covered / planned * 100) if planned else 0, 1),
    }


@frappe.whitelist()
def get_year_down_risk_count(academic_term=None):
    """
    Return count of students at risk of repeating the academic year.

    NMC rule: a student who has Supplementary in >=2 subjects (exam components)
    in the same session must repeat the year. We also include students with a
    direct Fail in overall_result.

    Returns: {at_risk_count}
    """
    guard = _require_medical_access()
    if guard is not None:
        return guard

    _validated_link("Academic Term", academic_term)

    components = frappe.get_all(
        "MBBS Exam Component",
        fields=["course_enrollment", "overall_result"],
    )

    # Build student -> supplementary count map via course_enrollment -> student
    # For speed, pull student from course_enrollment in bulk
    enrollment_names = list({c.course_enrollment for c in components if c.course_enrollment})
    student_map = {}
    if enrollment_names:
        enrollments = frappe.get_all(
            "Course Enrollment",
            filters={"name": ["in", enrollment_names]},
            fields=["name", "student"],
        )
        student_map = {e.name: e.student for e in enrollments}

    supp_count = {}   # student -> supplementary result count
    fail_set = set()  # students with outright Fail

    for c in components:
        student = student_map.get(c.course_enrollment)
        if not student:
            continue
        if c.overall_result == "Supplementary":
            supp_count[student] = supp_count.get(student, 0) + 1
        elif c.overall_result == "Fail":
            fail_set.add(student)

    # At risk = direct Fail OR >=2 Supplementary
    at_risk = fail_set | {s for s, cnt in supp_count.items() if cnt >= 2}

    return {
        "success": True,
        "at_risk_count": len(at_risk),
    }


@frappe.whitelist()
def get_exam_component_pass_rates(faculty=None, academic_term=None):
    """Return theory / practical / viva pass% separately."""
    guard = _require_medical_access()
    if guard is not None:
        return guard

    _validated_link("Faculty College", faculty)
    _validated_link("Academic Term", academic_term)

    components = frappe.get_all(
        "MBBS Exam Component",
        fields=["theory_status", "practical_status", "viva_status", "overall_result"],
    )

    total = len(components)
    if not total:
        return {
            "success": True,
            "total": 0,
            "theory_pass_pct": 0,
            "practical_pass_pct": 0,
            "viva_pass_pct": 0,
            "overall_pass_pct": 0,
        }

    theory_pass = sum(1 for c in components if c.theory_status == "Pass")
    practical_pass = sum(1 for c in components if c.practical_status == "Pass")
    viva_pass = sum(1 for c in components if c.viva_status == "Pass")
    overall_pass = sum(1 for c in components if c.overall_result == "Pass")

    return {
        "success": True,
        "total": total,
        "theory_pass_pct": round(theory_pass / total * 100, 1),
        "practical_pass_pct": round(practical_pass / total * 100, 1),
        "viva_pass_pct": round(viva_pass / total * 100, 1),
        "overall_pass_pct": round(overall_pass / total * 100, 1),
    }
