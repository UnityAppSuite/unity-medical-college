import frappe
from frappe.model.document import Document


class MBBSExamComponent(Document):
    def validate(self):
        for field in ("theory_ia", "theory_university", "practical_ia",
                      "practical_university", "viva_marks"):
            val = self.get(field)
            if val is not None and float(val) < 0:
                frappe.throw(f"{field} cannot be negative")
        self._derive_overall_result()

    def _derive_overall_result(self):
        statuses = [self.theory_status, self.practical_status, self.viva_status]
        if "Fail" in statuses:
            self.overall_result = "Fail"
        elif "Absent" in statuses:
            self.overall_result = "Supplementary"
        else:
            self.overall_result = "Pass"
