import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today


class TestMBBSOSCEAssessment(FrappeTestCase):

    def _make_stations(self, count=5, marks=15.0, max_marks=20.0):
        return [
            {
                "doctype": "MBBS OSCE Station Score",
                "station_no": i + 1,
                "station_type": "History",
                "marks_obtained": marks,
                "max_marks": max_marks,
                "examiner": "Test Examiner",
            }
            for i in range(count)
        ]

    def _make(self, **kwargs):
        student = frappe.db.get_value("Student", {}, "name")
        if not student:
            self.skipTest("No Student found in test DB")
        defaults = {
            "doctype": "MBBS OSCE Assessment",
            "student": student,
            "exam_date": today(),
            "station_count": 5,
            "pass_fail": "Pass",
            "station_scores": self._make_stations(5),
        }
        defaults.update(kwargs)
        return frappe.get_doc(defaults)

    def test_total_score_computed_on_validate(self):
        doc = self._make()
        doc.validate()
        self.assertAlmostEqual(doc.total_score, 5 * 15.0)

    def test_station_count_mismatch_raises(self):
        doc = self._make(station_count=3, station_scores=self._make_stations(5))
        with self.assertRaises(frappe.ValidationError):
            doc.validate()

    def test_zero_stations_with_count_zero_valid(self):
        doc = self._make(station_count=0, station_scores=[])
        doc.validate()
        self.assertEqual(doc.total_score, 0)
