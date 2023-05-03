// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["FIFO Stock Balance"] = {
	"filters": [
		{
			fieldtype: "Date",
			fieldname: "till_date",
			label: "Till Date",
			reqd: 1,
			default: frappe.datetime.get_today()
		},
		{
			fieldtype: "Link",
			fieldname: "item",
			label: "Item",
			options: "Item"
		},
		{
			fieldtype: "Link",
			fieldname: "item_group",
			label: "Item Group",
			options: "Item Group"
		},
		{
			fieldtype: "Link",
			fieldname: "warehouse",
			label: "Warehouse",
			options: "Warehouse"
			//reqd:1
		}
	]
};
