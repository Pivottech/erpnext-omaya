// Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Trial Balance for Party"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname": "fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"default": frappe.defaults.get_user_default("fiscal_year"),
			"reqd": 1,
			"on_change": function(query_report) {
				var fiscal_year = query_report.get_values().fiscal_year;
				if (!fiscal_year) {
					return;
				}
				frappe.model.with_doc("Fiscal Year", fiscal_year, function(r) {
					var fy = frappe.model.get_doc("Fiscal Year", fiscal_year);
					frappe.query_report.set_filter_value({
						from_date: fy.year_start_date,
						to_date: fy.year_end_date
					});
				});
			}
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.defaults.get_user_default("year_start_date"),
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.defaults.get_user_default("year_end_date"),
		},
		{
			"fieldname":"party_type",
			"label": __("Party Type"),
			"fieldtype": "Link",
			"options": "Party Type",
			"default": "Customer",
			"reqd": 1
		},
		{
			"fieldname":"party",
			"label": __("Party"),
			"fieldtype": "Dynamic Link",
			"get_options": function() {
				var party_type = frappe.query_report.get_filter_value('party_type');
				var party = frappe.query_report.get_filter_value('party');
				if(party && !party_type) {
					frappe.throw(__("Please select Party Type first"));
				}
				return party_type;
			}
		},
		{
			"fieldname": "account",
			"label": __("Account"),
			"fieldtype": "Link",
			"options": "Account",
			"get_query": function() {
				var company = frappe.query_report.get_filter_value('company');
				return {
					"doctype": "Account",
					"filters": {
						"company": company,
					}
				}
			}
		},
		{
			"fieldname": "show_zero_values",
			"label": __("Show zero values"),
			"fieldtype": "Check",
			"hidden": 1
		},
		{
			"fieldname": "show_opening",
			"fieldtype": "Check",
			"label": "Show Opening"
		},
		{
			"fieldname": "show_period_balance",
			"fieldtype": "Check",
			"label": "Show Period Balance"
		},
		{
			"fieldname": "show_zero_closing_values",
			"label": "Show Zero Closing Values",
			"fieldtype": "Check" 
		}
	],
	"formatter": function(value, row, column, data, default_formatter){
		if(data && column.fieldname == "party"){
			value = data.party || value;
			column.link_onclick = "open_general_ledger(" + JSON.stringify(data) + ")";
		}
		value = default_formatter(value, row, column, data);
		return value;
	}
}

function open_general_ledger (data) {
	if(!data.party) return;
	var win = window.open(`/desk#query-report/General Ledger`);
	win.onload = function(){
		win.frappe.route_options = {
			"party_type": frappe.query_report.get_filter_value('party_type'),
			"party": data.party,
			"company": frappe.query_report.get_filter_value('company'),
			"from_date": frappe.query_report.get_filter_value('from_date'),
			"to_date": frappe.query_report.get_filter_value('to_date'),
		};
		win.frappe.set_route("query-report", "General Ledger");
	}
}
