# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from erpnext.setup.doctype.item_group.item_group import get_child_item_groups

def execute(filters=None):
	columns, data = get_columns() ,get_data(filters)
	return columns, data

def get_data(filters):
	item_filters = {"is_stock_item": 1}
	if filters.item_group:
		item_filters.update({"item_group": ["in", get_child_item_groups(filters.item_group)]})
	if filters.item:
		item_filters.update({"item_code": filters.item})
	items = frappe.get_list("Item", filters=item_filters, pluck="name")
	sl_entries = []
	warehouse_condition = "and warehouse = '%s'"%filters.warehouse if filters.warehouse else ""
	for item in items:
		sl_entry = frappe.db.sql("""
		select  stock_queue, warehouse, stock_value, item_code from `tabStock Ledger Entry` sle1
		where sle1.is_cancelled=0 and sle1.item_code = %(item)s
		{warehouse_condition}
		and timestamp(sle1.posting_date, sle1.posting_time) = 
		(select max(timestamp(posting_date,posting_time)) from `tabStock Ledger Entry` sle2 where sle2.is_cancelled=0 and sle1.item_code = sle2.item_code
		and sle1.warehouse = sle2.warehouse and timestamp(sle2.posting_date,sle2.posting_time) <= timestamp(%(till_date)s, "23:59:59"))
		ORDER BY timestamp(sle1.posting_date, sle1.posting_time) DESC, sle1.creation DESC
		""".format(warehouse_condition=warehouse_condition), values={
			"item": item,
			"till_date": filters.till_date,
		}, as_dict=1, debug=1)
		sle_map = {}
		for sle in sl_entry:
			if not (sle.item_code, sle.warehouse) in sle_map:
				sle_map[(sle.item_code, sle.warehouse)] = 1
				sl_entries.append(sle)
	return sl_entries

def get_columns():
	return [
		{
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"label": "Item Code"
		},
		{
			"fieldname": "item_name",
			"fieldtype": "Data",
			"label": "Item Name",
			"hidden": 1
		},
		{
			"fieldname": "warehouse",
			"fieldtype": "Link",
			"options": "Warehouse",
			"label": "Warehouse"
		},
		{
			"fieldname": "stock_queue",
			"fieldtype": "Data",
			"label": "Stock Queue"
		},
		{
			"fieldname": "stock_value",
			"fieldtype": "Currency",
			"label": "Stock Value"
		},
	]	
