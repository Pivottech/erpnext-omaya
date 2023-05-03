from __future__ import unicode_literals
import frappe
#from erpnext.healthcare.utils import get_healthcare_services_to_invoice
from erpnext.stock.get_item_details import get_item_details
from erpnext.healthcare.doctype.healthcare_settings.healthcare_settings import get_receivable_account

@frappe.whitelist()
def get_appointments_to_invoice(patient, company):
    res = []
    patient_dms = frappe.get_list("Direct Medication Entry", filters = {"patient": patient, "company": company, "invoiced": False, "docstatus":1}, fields = ["name"])
    for p in patient_dms:
        dme = frappe.get_doc("Direct Medication Entry", p.name)
        for dme in dme.items:
            if not dme.invoiced:
                row = {
                    "service": dme.item_code,
                    "reference_type": "Direct Medication Entry Detail",
                    "reference_name": dme.name,
                    "qty": dme.qty
                }
                res.append(row)
    return res

def create_sales_invoice_for_healthcare(sales_invoice_type, patient, company, warehouse = None):
    from erpnext.healthcare.utils import get_healthcare_services_to_invoice
    customer = frappe.db.get_value("Patient", patient, "customer")
    items = []
    services = get_healthcare_services_to_invoice(patient, company) + get_appointments_to_invoice(patient, company)
    price_list, price_list_currency = frappe.db.get_values('Price List', {'selling': 1}, ['name', 'currency'])[0]
    for service in services:
        item = get_item_details({
            'doctype': 'Sales Invoice',
            'item_code': service.get("service"),
            'company': company,
            'warehouse': warehouse,
            'customer': customer,
            'selling_price_list': price_list,
            'price_list_currency': price_list_currency,
            'plc_conversion_rate': 1.0,
            'conversion_rate': 1.0
        })
        item.update({
            "doctype": "Sales Invoice Item",
            "qty": service.get("qty") or 1,
            "income_account": service.get("income_account"),
            "dt": service.get("reference_type"),
            "dn": service.get("reference_name"),
            "practitioner": service.get("practitioner")
        })
        items.append(item)
    si = frappe.new_doc("Sales Invoice")
    si.sales_invoice_type = sales_invoice_type
    si.customer = customer
    si.patient = patient
    si.company = company
    si.debit_to = get_receivable_account(company)
    for i in items:
        si.append("items", i)
    si.set_missing_values()
    si.insert()
    frappe.msgprint('Sales Invoice <a href="#Form/Journal Entry/%s" target="_blank">%s</a> Created'% (si.name, si.name))
    return si.name

def create_sales_invoice_for_lab_test(sales_invoice_type, patient, company, warehouse = None):
    from erpnext.healthcare.utils import get_lab_tests_to_invoice
    patient_obj = frappe.get_doc('Patient', patient)
    customer = frappe.db.get_value("Patient", patient, "customer")
    items = []
    services = get_lab_tests_to_invoice(patient_obj, company)
    price_list, price_list_currency = frappe.db.get_values('Price List', {'selling': 1}, ['name', 'currency'])[0]
    for service in services:
        item = get_item_details({
            'doctype': 'Sales Invoice',
            'item_code': service.get("service"),
            'company': company,
            'warehouse': warehouse,
            'customer': customer,
            'selling_price_list': price_list,
            'price_list_currency': price_list_currency,
            'plc_conversion_rate': 1.0,
            'conversion_rate': 1.0
        })
        item.update({
            "doctype": "Sales Invoice Item",
            "qty": service.get("qty") or 1,
            "income_account": service.get("income_account"),
            "dt": service.get("reference_type"),
            "dn": service.get("reference_name"),
            "practitioner": service.get("practitioner")
        })
        items.append(item)
    si = frappe.new_doc("Sales Invoice")
    si.sales_invoice_type = sales_invoice_type
    si.customer = customer
    si.patient = patient
    si.company = company
    si.debit_to = get_receivable_account(company)
    for i in items:
        si.append("items", i)
    si.set_missing_values()
    si.insert()
    frappe.msgprint('Sales Invoice <a href="#Form/Journal Entry/%s" target="_blank">%s</a> Created'% (si.name, si.name))
    return si.name
