import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today


class MBBSCaseLog(Document):
    def validate(self):
        if self.case_date and getdate(self.case_date) > getdate(today()):
            frappe.throw("Case Date cannot be in the future")
        if self.patient_age is not None:
            age = int(self.patient_age)
            if not (1 <= age <= 120):
                frappe.throw(f"Patient Age must be between 1 and 120, got {age}")
