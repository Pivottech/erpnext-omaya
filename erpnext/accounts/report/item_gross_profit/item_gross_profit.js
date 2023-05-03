// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Item Gross Profit"] = {
	"filters": [
		{
			fieldtype: "Link",
			fieldname: "sales_invoice",
			label: "Sales Invoice",
			options: "Sales Invoice",
			reqd: 1
		}
	]
};
