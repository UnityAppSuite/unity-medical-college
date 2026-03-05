import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today


class TestMBBSClinicalPosting(FrappeTestCase):

    def _make(self, **kwargs):
        defaults = {
            "doctype": "MBBS Clinical Posting",
            "student": frappe.db.get_value("Student", {}, "name"),
            "academic_year": frappe.db.get_value("Academic Year", {}, "name"),
            "department": frappe.db.get_value("Department", {}, "name"),
            "posting_type": "Compulsory",
            "start_date": today(),
            "end_date": add_days(today(), 14),
            "status": "Scheduled",
        }
        defaults.update(kwargs)
        if not all([defaults["student"], defaults["academic_year"], defaults["department"]]):
            self.skipTest("No Student/Academic Year/Department found in test DB")
        doc = frappe.get_doc(defaults)
        return doc

    def test_valid_posting_saves(self):
        doc = self._make()
        doc.validate()  # should not raise

    def test_end_date_before_start_raises(self):
        doc = self._make(start_date=today(), end_date=add_days(today(), -1))
        with self.assertRaises(frappe.ValidationError):
            doc.validate()

    def test_attendance_over_100_raises(self):
        doc = self._make(attendance_theory_pct=101)
        with self.assertRaises(frappe.ValidationError):
            doc.validate()

    def test_attendance_negative_raises(self):
        doc = self._make(attendance_clinical_pct=-1)
        with self.assertRaises(frappe.ValidationError):
            doc.validate()

    def test_attendance_boundary_values_valid(self):
        doc = self._make(attendance_theory_pct=0, attendance_clinical_pct=100)
        doc.validate()  # 0 and 100 are valid boundaries
