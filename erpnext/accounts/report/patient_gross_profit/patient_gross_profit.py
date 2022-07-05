# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_data(filters):
	data = []
	invoices = frappe.get_list("Sales Invoice", filters = {"status": "Paid", "docstatus": 1 , "posting_date": ["between", [filters.from_date, filters.till_date]]}, fields = ["name", "patient", "audit"])
	for invoice in invoices:
		if not invoice.patient:
			continue
		row = {"sales_invoice": invoice.name, "patient": invoice.patient, "audit": invoice.audit}
		items = frappe.get_list("Sales Invoice Item", filters = {"parent": invoice.name}, fields = ["reference_dt", "reference_dn", "base_amount", "practitioner_amount", "supplier_amount"])
		stock_entries_names = []
		practitioner_amounts = 0
		supplier_amounts = 0
		amounts = 0
		for item in items:
			practitioner_amounts += flt(item.practitioner_amount)
			supplier_amounts += flt(item.supplier_amount)
			amounts += flt(item.base_amount) 
			if item.reference_dt == "Direct Medication Entry Detail":
				parent = frappe.db.get_value(item.reference_dt, item.reference_dn, "parent")
				stock_entries_names += frappe.get_list("Stock Entry", filters = {"direct_medication_entry": parent, "docstatus": 1}, pluck = "name")
			elif item.reference_dt == "Clinical Procedure":
				se = frappe.db.get_value(item.reference_dt, item.reference_dn, "stock_entry")
				if se:
					stock_entries_names.append(se)
		differnt_amounts = -get_differnt_amounts(stock_entries_names)
		row.update({
			"cost": differnt_amounts,
			"practitioner_amount": practitioner_amounts,
			"supplier_amount": supplier_amounts,
			"amount": amounts,
			"gross_profit": amounts - practitioner_amounts - supplier_amounts - differnt_amounts
		})
		data.append(row)
	return data
		

def get_differnt_amounts(stock_entries_names):
	if stock_entries_names : 
		names = ",".join(["'%s'"] * len(stock_entries_names))%(tuple(stock_entries_names))
		sum = frappe.db.sql("""select sum(stock_value_difference) diff from `tabStock Ledger Entry`
		where voucher_type = "Stock Entry" and voucher_no in (%s)"""%names, as_dict = 1)
		if sum: 
			return sum[0].diff 
	return 0

def get_columns():
	return [
		{
			"fieldtype": "Link",
			"fieldname": "sales_invoice",
			"label": "Sales Invoice",
			"options": "Sales Invoice",
			"width": "150"
		},
		{
			"fieldtype": "Link",
			"fieldname": "patient",
			"label": "Patient",
			"options": "Patient",
			"width": "150"
		},
		{
			"fieldtype": "Currency",
			"fieldname": "amount",
			"label": "Amount",
			"width": "150"
		},
		{
			"fieldtype": "Currency",
			"fieldname": "cost",
			"label": "Cost",
			"width": "150"
		},
		{
			"fieldtype": "Currency",
			"fieldname": "practitioner_amount",
			"label": "Practitioner Amount",
			"width": "150"
		},
		{
			"fieldtype": "Currency",
			"fieldname": "supplier_amount",
			"label": "Supplier Amount",
			"width": "150"
		},
		{
			"fieldtype": "Currency",
			"fieldname": "gross_profit",
			"label": "Gross / Profit",
			"width": "150"
		},
		{
			"fieldtype": "Check",
			"fieldname": "audit",
			"label": "Audit",
			"width": "75"
		}
	]


