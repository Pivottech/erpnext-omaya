# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt, get_link_to_form
from erpnext.stock.utils import get_latest_stock_qty
from erpnext.healthcare.doctype.healthcare_settings.healthcare_settings import get_account

class DirectMedicationEntry(Document):

	def validate(self):
		self.validate_patient_inpatient_record()
		
	def validate_patient_inpatient_record(self):
		for entry in self.items:
			if not entry.patient: 
				entry.patient = self.patient
			if not entry.inpatient_record:
				entry.inpatient_record = self.inpatient_record
	def before_submit(self):
		self.delete_zero_items()

	def on_submit(self):
		success_msg = ""
		if self.update_stock:
			stock_entry = self.process_stock()
			if stock_entry:
				success_msg += _('Stock Entry {0} created and ').format(
					frappe.bold(get_link_to_form('Stock Entry', stock_entry)))
				self.db_set("stock_entry", stock_entry)
		if success_msg:
			frappe.msgprint(success_msg, title=_('Success'), indicator='green')
	
	def before_cancel(self):
		if self.stock_entry:
			self.cancel_stock_entry()
	
	def cancel_stock_entry(self):
		se = frappe.get_doc("Stock Entry", self.stock_entry)
		self.db_set("stock_entry", None)
		se.cancel()

	def process_stock(self):
		allow_negative_stock = frappe.db.get_single_value('Stock Settings', 'allow_negative_stock')
		if not allow_negative_stock:
			self.check_stock_qty()

		return self.make_stock_entry()

	def check_stock_qty(self):
		drug_shortage = get_drug_shortage_map(self.items, self.warehouse)

		if drug_shortage:
			message = _('Quantity not available for the following items in warehouse {0}. ').format(frappe.bold(self.warehouse))
			message += _('Please enable Allow Negative Stock in Stock Settings or create Stock Entry to proceed.')

			formatted_item_rows = ''

			for drug, shortage_qty in drug_shortage.items():
				item_link = get_link_to_form('Item', drug)
				formatted_item_rows += """
					<td>{0}</td>
					<td>{1}</td>
				</tr>""".format(item_link, frappe.bold(shortage_qty))

			message += """
				<table class='table'>
					<thead>
						<th>{0}</th>
						<th>{1}</th>
					</thead>
					{2}
				</table>
			""".format(_('Drug Code'), _('Shortage Qty'), formatted_item_rows)

			frappe.throw(message, title=_('Insufficient Stock'), is_minimizable=True, wide=True)
	
	def make_stock_entry(self):
		stock_entry = frappe.new_doc('Stock Entry')
		stock_entry.purpose = 'Material Issue'
		stock_entry.set_stock_entry_type()
		stock_entry.from_warehouse = self.warehouse
		stock_entry.company = self.company
		stock_entry.direct_medication_entry = self.name
		stock_entry.patient = self.patient
		cost_center = frappe.get_cached_value('Company',  self.company,  'cost_center')
		expense_account = frappe.db.get_value("Warehouse", self.warehouse, "expense_account")

		for entry in self.items:
			if frappe.db.get_value("Item", entry.item_code, "is_stock_item"):
				se_child = stock_entry.append('items')
				se_child.item_code = entry.item_code
				se_child.item_name = entry.item_name
				se_child.uom = frappe.db.get_value('Item', entry.item_code, 'stock_uom')
				se_child.stock_uom = se_child.uom
				se_child.qty = flt(entry.qty)
				# in stock uom
				se_child.conversion_factor = 1
				se_child.cost_center = cost_center
				# references
				se_child.patient = entry.patient
				se_child.expense_account = expense_account
		if stock_entry.get("items"):
			stock_entry.insert()
			stock_entry.submit()
			return stock_entry.name
		return None

	def check_invoiced(self):
		self.invoiced = True
		for i in self.items:
			if not i.invoiced:
				self.invoiced = False
				break
		self.db_update()

	@frappe.whitelist()
	def item_code_query(self):
		res = frappe.get_all("Bin", filters = {"warehouse": self.warehouse}, pluck = "item_code")
		res += frappe.get_all("Item", filters = {"is_stock_item": 0}, pluck = "name")

	def delete_zero_items(self):
		items = []
		for item in self.items:
			if item.qty:
				items.append(item)
			self.items = items

def get_drug_shortage_map(medication_orders, warehouse):
	"""
		Returns a dict like { item_code: shortage_qty }
	"""
	drug_requirement = dict()
	for d in medication_orders:
		if frappe.db.get_value("Item", d.item_code, "is_stock_item"):
			if not drug_requirement.get(d.item_code):
				drug_requirement[d.item_code] = 0
			drug_requirement[d.item_code] += flt(d.qty)

	drug_shortage = dict()
	for drug, required_qty in drug_requirement.items():
		available_qty = get_latest_stock_qty(drug, warehouse)
		if flt(required_qty) > flt(available_qty):
			drug_shortage[drug] = flt(flt(required_qty) - flt(available_qty))

	return drug_shortage

