import frappe
from frappe.tests.utils import FrappeTestCase


class TestMBBSExamComponent(FrappeTestCase):

    def _make(self, **kwargs):
        enrollment = frappe.db.get_value("Course Enrollment", {}, "name")
        if not enrollment:
            self.skipTest("No Course Enrollment found in test DB")
        defaults = {
            "doctype": "MBBS Exam Component",
            "course_enrollment": enrollment,
            "theory_ia": 25,
            "theory_university": 50,
            "practical_ia": 20,
            "practical_university": 40,
            "viva_marks": 20,
            "theory_status": "Pass",
            "practical_status": "Pass",
            "viva_status": "Pass",
            "overall_result": "Pass",
        }
        defaults.update(kwargs)
        return frappe.get_doc(defaults)

    def test_all_pass_gives_overall_pass(self):
        doc = self._make()
        doc.validate()
        self.assertEqual(doc.overall_result, "Pass")

    def test_one_fail_gives_overall_fail(self):
        doc = self._make(theory_status="Fail")
        doc.validate()
        self.assertEqual(doc.overall_result, "Fail")

    def test_one_absent_gives_supplementary(self):
        doc = self._make(practical_status="Absent")
        doc.validate()
        self.assertEqual(doc.overall_result, "Supplementary")

    def test_fail_takes_priority_over_absent(self):
        doc = self._make(theory_status="Fail", viva_status="Absent")
        doc.validate()
        self.assertEqual(doc.overall_result, "Fail")

    def test_negative_marks_raises(self):
        doc = self._make(theory_ia=-1)
        with self.assertRaises(frappe.ValidationError):
            doc.validate()
