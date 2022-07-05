// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Direct Medication Entry', {
	refresh: function (frm) {
		/*frm.set_query('item_code', 'items', function () {
			let items = null;
			frappe.call({
				method: "item_code_query",
				doc: frm.doc,
				callback: function (res) {
					items = res.message;
				},
				async: false
			});
			return {
				filters: [
					['Item', 'name', 'in', items]
				]
			}
			
		});*/
	},
	scan_barcode: function(frm){
		if (frm.doc.scan_barcode) {
			let transaction_controller= new erpnext.TransactionController({frm:frm});
			transaction_controller.scan_barcode();
		}
	}
});
frappe.ui.form.on('Direct Medication Entry Detail', {
	item_code: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		if(d.item_code) {
			frappe.db.get_value("Item", d.item_code,"item_name").then(item_name => {
				d.item_name = item_name.message.item_name;
				frm.refresh_fields("items");
			});
		}
	}
});