# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.accounts.general_ledger import make_reverse_gl_entries
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
from erpnext.accounts.utils import unlink_ref_doc_from_payment_entries

class ServiceInvoice(AccountsController):
	def on_submit(self):
		self.make_gl_entries()
		self.make_payment()
	
	def validate(self):
		pass

	def make_gl_entries(self):
		cost_center = frappe.db.get_value('Company', self.company, ['cost_center'])
		gl_dict = []
		for service in self.services:
			gl_dict.append(self.get_gl_dict({
				"account": service.account,
				"against": self.customer,
				"credit": service.amount,
				"credit_in_account_currency": service.amount,
				"cost_center": cost_center
			},item=self))
		gl_dict.append(self.get_gl_dict({
			"account": self.receivable_account,
			"party_type": "Customer",
			"party": self.customer,
			"debit": self.grand_total,
			"debit_in_account_currency": self.grand_total,
			"cost_center": cost_center,
			"against_voucher": self.name,
			"against_voucher_type": self.doctype
		},item=self))
		from erpnext.accounts.general_ledger import make_gl_entries
		make_gl_entries(gl_dict,cancel=(self.docstatus == 2),update_outstanding="Yes",merge_entries=True)
	
	def on_cancel(self):
		unlink_ref_doc_from_payment_entries(self)
		make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)
		self.ignore_linked_doctypes = ('GL Entry')

	def make_payment(self):
		payment = get_payment_entry(self.doctype , self.name)
		for ref in payment.references : 
			if ref.reference_name == self.name:
				ref.allocated_amount = self.paid_amount
		payment.save()
		payment.submit()
		

	
	@frappe.whitelist()
	def get_item_account(self , item):
		return frappe.db.get_value('Item Default', {'parent':item , 'Company':self.company}, ['income_account'])
