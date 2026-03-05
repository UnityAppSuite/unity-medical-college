"""
NMC Compliance API — faculty strength and syllabus coverage reports.

All functions gate on _require_medical_access() (module enabled + read permission).
"""

import frappe
from unity_medical_college.unity_medical_college.doctype.medical_college_settings.medical_college_settings import (
    is_medical_enabled,
)


def _disabled():
    return {"success": False, "message": "Medical module not configured", "data": []}


def _require_medical_access():
    if not is_medical_enabled():
        return _disabled()
    frappe.has_permission("Medical College Settings", "read", throw=True)
    return None


def _validated_link(doctype, value):
    if value and not frappe.db.exists(doctype, value):
        frappe.throw(
            f"Invalid {doctype}: {frappe.utils.escape_html(str(value))}",
            frappe.ValidationError,
        )
    return value or None


@frappe.whitelist()
def get_nmc_compliance_report(faculty=None):
    """Return student-wise attendance eligibility table."""
    guard = _require_medical_access()
    if guard is not None:
        return guard

    _validated_link("Faculty College", faculty)

    theory_threshold = (
        frappe.db.get_single_value("Medical College Settings", "theory_attendance_threshold") or 75
    )
    clinical_threshold = (
        frappe.db.get_single_value("Medical College Settings", "clinical_attendance_threshold") or 75
    )

    postings = frappe.get_all(
        "MBBS Clinical Posting",
        fields=[
            "student",
            "department",
            "academic_year",
            "attendance_theory_pct",
            "attendance_clinical_pct",
            "status",
        ],
        order_by="student asc",
    )

    rows = []
    for p in postings:
        theory_ok = (p.attendance_theory_pct or 0) >= theory_threshold
        clinical_ok = (p.attendance_clinical_pct or 0) >= clinical_threshold
        rows.append(
            {
                "student": p.student,
                "department": p.department,
                "academic_year": p.academic_year,
                "attendance_theory_pct": p.attendance_theory_pct or 0,
                "attendance_clinical_pct": p.attendance_clinical_pct or 0,
                "theory_eligible": theory_ok,
                "clinical_eligible": clinical_ok,
                "eligible": theory_ok and clinical_ok,
            }
        )

    ineligible = [r for r in rows if not r["eligible"]]

    return {
        "success": True,
        "total_students": len(set(r["student"] for r in rows)),
        "ineligible_count": len(set(r["student"] for r in ineligible)),
        "rows": rows,
    }


@frappe.whitelist()
def get_faculty_strength_report(faculty=None):
    """Return department-wise actual vs NMC-required faculty strength."""
    guard = _require_medical_access()
    if guard is not None:
        return guard

    _validated_link("Faculty College", faculty)

    records = frappe.get_all(
        "NMC Faculty Compliance",
        fields=[
            "department",
            "academic_year",
            "required_professors",
            "required_assoc_prof",
            "required_asst_prof",
            "actual_professors",
            "actual_assoc_prof",
            "actual_asst_prof",
            "compliant",
            "shortfall_note",
        ],
        order_by="department asc",
    )

    for r in records:
        r["required_total"] = (
            (r.required_professors or 0)
            + (r.required_assoc_prof or 0)
            + (r.required_asst_prof or 0)
        )
        r["actual_total"] = (
            (r.actual_professors or 0)
            + (r.actual_assoc_prof or 0)
            + (r.actual_asst_prof or 0)
        )

    non_compliant = [r for r in records if not r["compliant"]]

    return {
        "success": True,
        "total_departments": len(records),
        "non_compliant_count": len(non_compliant),
        "rows": records,
    }


@frappe.whitelist()
def get_syllabus_coverage(course_offering=None):
    """Compare Teaching Records vs Curriculum Map for a course offering."""
    guard = _require_medical_access()
    if guard is not None:
        return guard

    if not course_offering:
        frappe.throw("course_offering is required", frappe.ValidationError)

    _validated_link("Course Offering", course_offering)

    planned = frappe.db.count("Curriculum Map", filters={"course_offering": course_offering})
    covered = frappe.db.count("Teaching Record", filters={"course_offering": course_offering})
    coverage_pct = round((covered / planned * 100) if planned else 0, 1)

    return {
        "success": True,
        "course_offering": course_offering,
        "planned": planned,
        "covered": covered,
        "coverage_pct": coverage_pct,
    }
