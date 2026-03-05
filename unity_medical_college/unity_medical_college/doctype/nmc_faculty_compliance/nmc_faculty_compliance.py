import frappe
from frappe.model.document import Document


class NMCFacultyCompliance(Document):
    def validate(self):
        for field in ("required_professors", "required_assoc_prof", "required_asst_prof",
                      "actual_professors", "actual_assoc_prof", "actual_asst_prof"):
            val = self.get(field)
            if val is not None and int(val) < 0:
                frappe.throw(f"{field} cannot be negative")
        self._derive_compliance()

    def _derive_compliance(self):
        self.compliant = int(
            (self.actual_professors or 0) >= (self.required_professors or 0)
            and (self.actual_assoc_prof or 0) >= (self.required_assoc_prof or 0)
            and (self.actual_asst_prof or 0) >= (self.required_asst_prof or 0)
        )
        if not self.compliant:
            parts = []
            if (self.actual_professors or 0) < (self.required_professors or 0):
                parts.append(f"Professors: need {self.required_professors}, have {self.actual_professors or 0}")
            if (self.actual_assoc_prof or 0) < (self.required_assoc_prof or 0):
                parts.append(f"Assoc Prof: need {self.required_assoc_prof}, have {self.actual_assoc_prof or 0}")
            if (self.actual_asst_prof or 0) < (self.required_asst_prof or 0):
                parts.append(f"Asst Prof: need {self.required_asst_prof}, have {self.actual_asst_prof or 0}")
            if parts and not self.shortfall_note:
                self.shortfall_note = "; ".join(parts)
        else:
            self.shortfall_note = self.shortfall_note or ""
