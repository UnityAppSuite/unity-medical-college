"""
Unit tests for medical module APIs.

Tests are grouped by concern:
  - TestMedicalGate: is_medical_enabled() and check_medical_enabled()
  - TestClinicalAPIDisabled: all 7 functions gate correctly when module off
  - TestClinicalAPIEnabled: all 7 functions return success=True with expected keys
  - TestClinicalAPIInputValidation: bad link-field values raise ValidationError
  - TestNMCAPIDisabled: all 3 NMC functions gate correctly
  - TestNMCAPIEnabled: all 3 NMC functions return expected shape
"""

import frappe
from frappe.tests.utils import FrappeTestCase


def _enable_medical():
    frappe.db.set_single_value("Medical College Settings", "enable_medical_module", 1)
    frappe.db.commit()


def _disable_medical():
    frappe.db.set_single_value("Medical College Settings", "enable_medical_module", 0)
    frappe.db.commit()


# ---------------------------------------------------------------------------
# Gate tests
# ---------------------------------------------------------------------------

class TestMedicalGate(FrappeTestCase):
    """is_medical_enabled() and check_medical_enabled() behave correctly."""

    def setUp(self):
        _disable_medical()

    def tearDown(self):
        _disable_medical()

    def test_disabled_by_default(self):
        from unity_medical_college.unity_medical_college.doctype.medical_college_settings.medical_college_settings import (
            is_medical_enabled,
        )
        self.assertFalse(is_medical_enabled())

    def test_enabled_after_set(self):
        from unity_medical_college.unity_medical_college.doctype.medical_college_settings.medical_college_settings import (
            is_medical_enabled,
        )
        _enable_medical()
        self.assertTrue(is_medical_enabled())

    def test_check_medical_enabled_whitelisted(self):
        from unity_medical_college.unity_medical_college.dashboard_api.clinical_api import check_medical_enabled
        _enable_medical()
        self.assertTrue(check_medical_enabled())


# ---------------------------------------------------------------------------
# Clinical API — disabled state
# ---------------------------------------------------------------------------

class TestClinicalAPIDisabled(FrappeTestCase):
    """All clinical API functions return success=False when module is off."""

    def setUp(self):
        _disable_medical()

    def tearDown(self):
        _disable_medical()

    def _assert_disabled(self, result):
        self.assertFalse(result.get("success"))
        self.assertEqual(result.get("message"), "Medical module not configured")

    def test_get_nmc_attendance_compliance_disabled(self):
        from unity_medical_college.unity_medical_college.dashboard_api.clinical_api import get_nmc_attendance_compliance
        self._assert_disabled(get_nmc_attendance_compliance())

    def test_get_clinical_posting_summary_disabled(self):
        from unity_medical_college.unity_medical_college.dashboard_api.clinical_api import get_clinical_posting_summary
        self._assert_disabled(get_clinical_posting_summary())

    def test_get_case_log_compliance_disabled(self):
        from unity_medical_college.unity_medical_college.dashboard_api.clinical_api import get_case_log_compliance
        self._assert_disabled(get_case_log_compliance())

    def test_get_osce_summary_disabled(self):
        from unity_medical_college.unity_medical_college.dashboard_api.clinical_api import get_osce_summary
        self._assert_disabled(get_osce_summary())

    def test_get_batch_phase_distribution_disabled(self):
        from unity_medical_college.unity_medical_college.dashboard_api.clinical_api import get_batch_phase_distribution
        self._assert_disabled(get_batch_phase_distribution())

    def test_get_exam_component_pass_rates_disabled(self):
        from unity_medical_college.unity_medical_college.dashboard_api.clinical_api import get_exam_component_pass_rates
        self._assert_disabled(get_exam_component_pass_rates())

    def test_check_medical_enabled_returns_false(self):
        from unity_medical_college.unity_medical_college.dashboard_api.clinical_api import check_medical_enabled
        self.assertFalse(check_medical_enabled())

    def test_get_faculty_nmc_compliance_summary_disabled(self):
        from unity_medical_college.unity_medical_college.dashboard_api.clinical_api import get_faculty_nmc_compliance_summary
        self._assert_disabled(get_faculty_nmc_compliance_summary())

    def test_get_curriculum_coverage_summary_disabled(self):
        from unity_medical_college.unity_medical_college.dashboard_api.clinical_api import get_curriculum_coverage_summary
        self._assert_disabled(get_curriculum_coverage_summary())

    def test_get_year_down_risk_count_disabled(self):
        from unity_medical_college.unity_medical_college.dashboard_api.clinical_api import get_year_down_risk_count
        self._assert_disabled(get_year_down_risk_count())


# ---------------------------------------------------------------------------
# Clinical API — enabled state
# ---------------------------------------------------------------------------

class TestClinicalAPIEnabled(FrappeTestCase):
    """All clinical API functions return success=True with expected keys when on."""

    def setUp(self):
        _enable_medical()

    def tearDown(self):
        _disable_medical()

    def test_get_nmc_attendance_compliance_shape(self):
        from unity_medical_college.unity_medical_college.dashboard_api.clinical_api import get_nmc_attendance_compliance
        result = get_nmc_attendance_compliance()
        self.assertTrue(result.get("success"))
        self.assertIn("ineligible_count", result)
        self.assertIn("eligible_count", result)   # NEW
        self.assertIn("total", result)             # NEW
        self.assertIn("theory_threshold", result)
        self.assertIn("clinical_threshold", result)
        self.assertIn("department_breakdown", result)
        self.assertIsInstance(result["department_breakdown"], list)
        # eligible_count + ineligible_count <= total (some students may be in both categories)
        self.assertGreaterEqual(result["total"], result["ineligible_count"])

    def test_get_clinical_posting_summary_shape(self):
        from unity_medical_college.unity_medical_college.dashboard_api.clinical_api import get_clinical_posting_summary
        result = get_clinical_posting_summary()
        self.assertTrue(result.get("success"))
        self.assertIn("total_active", result)
        self.assertIn("by_department", result)

    def test_get_case_log_compliance_shape(self):
        from unity_medical_college.unity_medical_college.dashboard_api.clinical_api import get_case_log_compliance
        result = get_case_log_compliance()
        self.assertTrue(result.get("success"))
        self.assertIn("expected", result)
        self.assertIn("submitted", result)
        self.assertIn("compliance_pct", result)

    def test_get_osce_summary_shape(self):
        from unity_medical_college.unity_medical_college.dashboard_api.clinical_api import get_osce_summary
        result = get_osce_summary()
        self.assertTrue(result.get("success"))
        self.assertIn("total", result)
        self.assertIn("passed", result)
        self.assertIn("failed", result)
        self.assertIn("pending_count", result)   # NEW
        self.assertIn("pass_pct", result)
        # total = passed + failed + pending
        self.assertEqual(result["total"], result["passed"] + result["failed"] + result["pending_count"])

    def test_get_batch_phase_distribution_shape(self):
        from unity_medical_college.unity_medical_college.dashboard_api.clinical_api import get_batch_phase_distribution
        result = get_batch_phase_distribution()
        self.assertTrue(result.get("success"))
        self.assertIn("phases", result)
        self.assertIsInstance(result["phases"], list)

    def test_get_exam_component_pass_rates_shape(self):
        from unity_medical_college.unity_medical_college.dashboard_api.clinical_api import get_exam_component_pass_rates
        result = get_exam_component_pass_rates()
        self.assertTrue(result.get("success"))
        for key in ("total", "theory_pass_pct", "practical_pass_pct", "viva_pass_pct", "overall_pass_pct"):
            self.assertIn(key, result)

    def test_compliance_pct_in_range(self):
        from unity_medical_college.unity_medical_college.dashboard_api.clinical_api import get_case_log_compliance
        result = get_case_log_compliance()
        pct = result.get("compliance_pct", 0)
        self.assertGreaterEqual(pct, 0)
        self.assertLessEqual(pct, 100)

    def test_get_faculty_nmc_compliance_summary_shape(self):
        from unity_medical_college.unity_medical_college.dashboard_api.clinical_api import get_faculty_nmc_compliance_summary
        result = get_faculty_nmc_compliance_summary()
        self.assertTrue(result.get("success"))
        self.assertIn("compliant_depts", result)
        self.assertIn("total_depts", result)
        self.assertIn("compliance_pct", result)
        self.assertGreaterEqual(result["compliance_pct"], 0)
        self.assertLessEqual(result["compliance_pct"], 100)
        self.assertGreaterEqual(result["total_depts"], result["compliant_depts"])

    def test_get_curriculum_coverage_summary_shape(self):
        from unity_medical_college.unity_medical_college.dashboard_api.clinical_api import get_curriculum_coverage_summary
        result = get_curriculum_coverage_summary()
        self.assertTrue(result.get("success"))
        self.assertIn("planned", result)
        self.assertIn("covered", result)
        self.assertIn("coverage_pct", result)
        self.assertGreaterEqual(result["coverage_pct"], 0)
        self.assertLessEqual(result["coverage_pct"], 100)
        self.assertGreaterEqual(result["planned"], result["covered"])

    def test_get_year_down_risk_count_shape(self):
        from unity_medical_college.unity_medical_college.dashboard_api.clinical_api import get_year_down_risk_count
        result = get_year_down_risk_count()
        self.assertTrue(result.get("success"))
        self.assertIn("at_risk_count", result)
        self.assertGreaterEqual(result["at_risk_count"], 0)


# ---------------------------------------------------------------------------
# Clinical API — input validation
# ---------------------------------------------------------------------------

class TestClinicalAPIInputValidation(FrappeTestCase):
    """Invalid link-field values raise ValidationError."""

    def setUp(self):
        _enable_medical()

    def tearDown(self):
        _disable_medical()

    def test_invalid_academic_term_raises(self):
        from unity_medical_college.unity_medical_college.dashboard_api.clinical_api import get_nmc_attendance_compliance
        with self.assertRaises(frappe.ValidationError):
            get_nmc_attendance_compliance(academic_term="NONEXISTENT_TERM_XYZ_999")

    def test_invalid_faculty_raises(self):
        from unity_medical_college.unity_medical_college.dashboard_api.clinical_api import get_clinical_posting_summary
        with self.assertRaises(frappe.ValidationError):
            get_clinical_posting_summary(faculty="NONEXISTENT_FACULTY_XYZ_999")

    def test_none_params_do_not_raise(self):
        from unity_medical_college.unity_medical_college.dashboard_api.clinical_api import get_osce_summary
        result = get_osce_summary(faculty=None, academic_term=None)
        self.assertTrue(result.get("success"))

    def test_syllabus_coverage_missing_course_offering_raises(self):
        from unity_medical_college.unity_medical_college.dashboard_api.nmc_api import get_syllabus_coverage
        with self.assertRaises(frappe.ValidationError):
            get_syllabus_coverage(course_offering=None)


# ---------------------------------------------------------------------------
# NMC API — disabled state
# ---------------------------------------------------------------------------

class TestNMCAPIDisabled(FrappeTestCase):

    def setUp(self):
        _disable_medical()

    def tearDown(self):
        _disable_medical()

    def _assert_disabled(self, result):
        self.assertFalse(result.get("success"))

    def test_get_nmc_compliance_report_disabled(self):
        from unity_medical_college.unity_medical_college.dashboard_api.nmc_api import get_nmc_compliance_report
        self._assert_disabled(get_nmc_compliance_report())

    def test_get_faculty_strength_report_disabled(self):
        from unity_medical_college.unity_medical_college.dashboard_api.nmc_api import get_faculty_strength_report
        self._assert_disabled(get_faculty_strength_report())

    def test_get_syllabus_coverage_disabled(self):
        from unity_medical_college.unity_medical_college.dashboard_api.nmc_api import get_syllabus_coverage
        self._assert_disabled(get_syllabus_coverage(course_offering="test"))


# ---------------------------------------------------------------------------
# NMC API — enabled state
# ---------------------------------------------------------------------------

class TestNMCAPIEnabled(FrappeTestCase):

    def setUp(self):
        _enable_medical()

    def tearDown(self):
        _disable_medical()

    def test_get_nmc_compliance_report_shape(self):
        from unity_medical_college.unity_medical_college.dashboard_api.nmc_api import get_nmc_compliance_report
        result = get_nmc_compliance_report()
        self.assertTrue(result.get("success"))
        self.assertIn("total_students", result)
        self.assertIn("ineligible_count", result)
        self.assertIn("rows", result)
        self.assertIsInstance(result["rows"], list)

    def test_get_faculty_strength_report_shape(self):
        from unity_medical_college.unity_medical_college.dashboard_api.nmc_api import get_faculty_strength_report
        result = get_faculty_strength_report()
        self.assertTrue(result.get("success"))
        self.assertIn("total_departments", result)
        self.assertIn("non_compliant_count", result)
        self.assertIn("rows", result)

    def test_get_syllabus_coverage_invalid_offering_raises(self):
        from unity_medical_college.unity_medical_college.dashboard_api.nmc_api import get_syllabus_coverage
        with self.assertRaises(frappe.ValidationError):
            get_syllabus_coverage(course_offering="NONEXISTENT_OFFERING_XYZ")
