import frappe
from frappe.tests.utils import FrappeTestCase


class TestNMCFacultyCompliance(FrappeTestCase):

    def _make(self, **kwargs):
        dept = frappe.db.get_value("Department", {}, "name")
        ay = frappe.db.get_value("Academic Year", {}, "name")
        if not dept or not ay:
            self.skipTest("No Department/Academic Year found in test DB")
        defaults = {
            "doctype": "NMC Faculty Compliance",
            "department": dept,
            "academic_year": ay,
            "required_professors": 2,
            "required_assoc_prof": 2,
            "required_asst_prof": 3,
            "actual_professors": 2,
            "actual_assoc_prof": 2,
            "actual_asst_prof": 3,
        }
        defaults.update(kwargs)
        return frappe.get_doc(defaults)

    def test_meets_norms_compliant(self):
        doc = self._make()
        doc.validate()
        self.assertEqual(doc.compliant, 1)

    def test_below_professors_not_compliant(self):
        doc = self._make(actual_professors=1)
        doc.validate()
        self.assertEqual(doc.compliant, 0)

    def test_shortfall_note_auto_populated(self):
        doc = self._make(actual_professors=1, shortfall_note="")
        doc.validate()
        self.assertIn("Professors", doc.shortfall_note)

    def test_negative_count_raises(self):
        doc = self._make(actual_professors=-1)
        with self.assertRaises(frappe.ValidationError):
            doc.validate()

    def test_fully_compliant_clears_nothing_when_note_set(self):
        doc = self._make(shortfall_note="Manually set note")
        doc.validate()
        self.assertEqual(doc.compliant, 1)
