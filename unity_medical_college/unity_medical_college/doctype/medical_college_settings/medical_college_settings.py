import frappe
from frappe.model.document import Document


class MedicalCollegeSettings(Document):
    pass


def is_medical_enabled():
    """Return True if the medical module is enabled in settings."""
    return bool(frappe.db.get_single_value("Medical College Settings", "enable_medical_module"))
