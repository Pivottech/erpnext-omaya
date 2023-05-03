# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt

def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data

def get_data(filters):
	data = []
	items = frappe.get_list("Sales Invoice Item", filters = {"parent": filters.get("sales_invoice")}, fields = ["item_code","item_name","supplier_amount", "practitioner_amount", "base_amount", "reference_dt", "reference_dn"], order_by="idx")
	for item in items:
		stock_entries = []
		if item.reference_dt == "Direct Medication Entry Detail":
			parent = frappe.db.get_value(item.reference_dt, item.reference_dn, "parent")
			stock_entries = frappe.get_list("Stock Entry", filters = {"direct_medication_entry": parent, "docstatus": 1}, pluck = "name")
		elif item.reference_dt == "Clinical Procedure":
			stock_entries = [frappe.db.get_value(item.reference_dt, item.reference_dn, "stock_entry")]
		stock_diff = frappe.get_list("Stock Ledger Entry", filters={
			"voucher_type": "Stock Entry",
			"voucher_no": ["in", stock_entries],
			"item_code": item.item_code
		}, fields=["sum(stock_value_difference) as diff"])[0]["diff"] or 0
		stock_diff *= -1
		total_cost = stock_diff + flt(item.supplier_amount) + flt(item.practitioner_amount)
		profit = flt(item.base_amount) - total_cost
		data.append({
			"item": "%s:%s"%(item.item_code, item.item_name),
			"amount": item.base_amount,
			"cost": stock_diff,
			"supplier_amount": item.supplier_amount,
			"practitioner_amount": item.practitioner_amount,
			"profit": profit,
			"profit_percent": profit * 100 / flt(item.base_amount) if item.base_amount else 0
		})
	return data

def get_columns():
	return [
		{
			"fieldname": "item",
			"fieldtype": "data",
			"label": "Item"
		},
		{
			"fieldname": "amount",
			"fieldtype": "Currency",
			"label": "Amount"
		},
		{
			"fieldname": "cost",
			"fieldtype": "Currency",
			"label": "Cost"
		},
		{
			"fieldname": "supplier_amount",
			"fieldtype": "Currency",
			"label": "Supplier Amount"
		},
		{
			"fieldname": "practitioner_amount",
			"fieldtype": "Currency",
			"label": "Practitioner Amount"
		},
		{
			"fieldname": "profit",
			"fieldtype": "Currency",
			"label": "Profit"
		},
		{
			"fieldname": "profit_percent",
			"fieldtype": "Percent",
			"label": "Profit %"
		}
	]
	
