// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Patient Gross Profit"] = {
	"filters": [
		{
			fieldtype: "Date",
			fieldname: "from_date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			label: "From Date"
		},
		{
			fieldtype: "Date",
			fieldname: "till_date",
			default: frappe.datetime.get_today(),
			label: "Till Date"
		}

	]
};
