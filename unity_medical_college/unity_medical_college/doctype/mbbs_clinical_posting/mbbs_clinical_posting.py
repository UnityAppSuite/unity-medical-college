import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today


class MBBSClinicalPosting(Document):
    def validate(self):
        if self.end_date and self.start_date:
            if getdate(self.end_date) < getdate(self.start_date):
                frappe.throw("End Date cannot be before Start Date")
        for field in ("attendance_theory_pct", "attendance_clinical_pct"):
            val = self.get(field)
            if val is not None and not (0 <= float(val) <= 100):
                frappe.throw(f"{field} must be between 0 and 100, got {val}")
