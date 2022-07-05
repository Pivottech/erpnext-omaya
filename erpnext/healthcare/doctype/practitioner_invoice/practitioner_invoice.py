# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.accounts.general_ledger import make_reverse_gl_entries

class PractitionerInvoice(AccountsController):
	def on_submit(self):
		self.mark_sales_invoice_item_as_invoiced()
		self.make_gl_entries()
	
	def validate(self):
		self.validate_cost_center()
		self.validate_expense_account()
		self.validate_total_amount()


	def validate_cost_center(self):
		for item in self.items:
			if not item.cost_center:
				item.cost_center = self.cost_center
	def validate_expense_account(self):
		for item in self.items:
			if not item.expense_account:
				item.expense_account = self.expense_account

	def validate_total_amount(self):
		total_amount = 0 
		for item in self.items:
			total_amount += flt(item.amount)
		self.total_amount = total_amount

	def mark_sales_invoice_item_as_invoiced(self):
		for item in self.items:
			sales_invoice_item = frappe.get_doc('Sales Invoice Item' , item.sales_invoice_item_name)
			sales_invoice_item.invoiced = self.docstatus == 1
			sales_invoice_item.db_update()

	def make_gl_entries(self):
		from erpnext.accounts.general_ledger import make_gl_entries
		for item in self.items:
			expense_gl_entry = self.get_gl_dict({
				"account" : item.expense_account,
				"against" : self.practitioner_account,
				"cost_center" : item.cost_center,
				"debit" : item.amount,
				"debit_in_account_currency" : item.amount 
			},item=self)
			practitioner_gl_entry = self.get_gl_dict({
				"account" : self.practitioner_account,
				"against" : item.expense_account,
				#"cost_center" : item.cost_center,
				"party_type" : "Employee",
				"party" : self.employee,
				"credit" : item.amount,
				"credit_in_account_currency" : item.amount,
				"against_voucher" : self.name,
				"against_voucher_type" : "Practitioner Invoice"
			},item=self)
			
			make_gl_entries([practitioner_gl_entry, expense_gl_entry], cancel=(self.docstatus == 2),update_outstanding="Yes", merge_entries=False)
	
	def on_cancel(self):
		self.ignore_linked_doctypes = ('GL Entry', 'Stock Ledger Entry')
		self.mark_sales_invoice_item_as_invoiced()
		make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)
