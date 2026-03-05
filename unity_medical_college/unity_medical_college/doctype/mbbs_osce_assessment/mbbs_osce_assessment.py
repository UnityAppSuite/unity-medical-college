import frappe
from frappe.model.document import Document


class MBBSOSCEAssessment(Document):
    def validate(self):
        stations = self.get("station_scores") or []
        if self.station_count and len(stations) != int(self.station_count):
            frappe.throw(
                f"Station Count is {self.station_count} but {len(stations)} station score rows found"
            )
        self.total_score = sum((row.marks_obtained or 0) for row in stations)
