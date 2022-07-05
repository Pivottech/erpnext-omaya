// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Practitioner Invoice Item', {
	items_remove: function (frm, cdt, cdn) { calc_total_amount(); },
	amount: function (frm, cdt, cdn) { calc_total_amount(); },
});

frappe.ui.form.on('Practitioner Invoice', {
	onload:function(frm) {
		frm.set_query('expense_account',function(){
		   return{
               'filters':[
                   ['Account','is_group',"=",false],
                   ['Account','account_type','=','Expense Account']
               ]
           }; 
		});
		frm.set_query('practitioner_account',function(){
		   return{
               'filters':[
                   ['Account','is_group',"=",false],
                   ['Account','account_type','=','Payabal']
               ]
           }; 
		});		
	},

	refresh: function(frm) {
		if(frm.doc.docstatus > 0) {
			frm.add_custom_button(__('Accounting Ledger'), function() {
				frappe.route_options = {
					voucher_no: frm.doc.name,
					from_date: frm.doc.posting_date,
					to_date: moment(frm.doc.modified).format('YYYY-MM-DD'),
					company: frm.doc.company,
					group_by: '',
					show_cancelled_entries: frm.doc.docstatus === 2
				};
				frappe.set_route("query-report", "General Ledger");
			}, __("View"));}
	}


})

function calc_total_amount() {
	var total_amount = 0;
	for (var i = 0; i < cur_frm.doc.items.length; i++){
		total_amount += cur_frm.doc.items[i].amount;
	}
	cur_frm.doc.total_amount = total_amount;
	cur_frm.refresh_fields('total_amount');
}
