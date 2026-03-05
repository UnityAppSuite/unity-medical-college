import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today


class TestMBBSCaseLog(FrappeTestCase):

    def _make(self, **kwargs):
        defaults = {
            "doctype": "MBBS Case Log",
            "student": frappe.db.get_value("Student", {}, "name"),
            "case_date": today(),
            "patient_age": 35,
            "patient_gender": "Male",
            "case_type": "Observed",
        }
        defaults.update(kwargs)
        if not defaults["student"]:
            self.skipTest("No Student found in test DB")
        return frappe.get_doc(defaults)

    def test_valid_case_log_saves(self):
        doc = self._make()
        doc.validate()

    def test_future_case_date_raises(self):
        doc = self._make(case_date=add_days(today(), 1))
        with self.assertRaises(frappe.ValidationError):
            doc.validate()

    def test_age_zero_raises(self):
        doc = self._make(patient_age=0)
        with self.assertRaises(frappe.ValidationError):
            doc.validate()

    def test_age_over_120_raises(self):
        doc = self._make(patient_age=121)
        with self.assertRaises(frappe.ValidationError):
            doc.validate()

    def test_age_boundary_valid(self):
        doc = self._make(patient_age=120)
        doc.validate()
