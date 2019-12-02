# Copyright (c) 2013, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json

from frappe.utils import flt, cint, getdate
from frappe import _, scrub
import datetime
from datetime import datetime
import pandas as pd
import os

from erpnext.stock.report.stock_balance.stock_balance import (get_stock_ledger_entries, get_item_details)
from erpnext.accounts.utils import get_fiscal_year
from six import iteritems

def execute(filters=None):
	'''Funcion especial ejecutada por frappe para generar la data para el reporte'''
	
	# Find journal entries for specified time period
	# Find journal entry accounts that belong to the time period filtered journal entries
	# From journal entry accounts, Create a list of journal entry names and dates of journal
	
	get_journal_entries()
	get_payment_entries()
	
	
	# DEV  Getting filters to verify
	filters = frappe._dict(filters or {})
	# DEV get the dates in datetime object form
	dev_from_date, dev_to_date = getdate(filters.from_date), getdate(filters.to_date)
	# DEV Write the file to see what we are getting.
	# write_file(dev_from_date, 'develop_filters')
	write_file(get_period_date_ranges(filters), 'develop_date_ranges')
	
	columns = get_columns(filters)
	write_file(columns, 'develop_columns')

	data = [{
		"total": 0,
		"name": "<b>Saldo Inicial</b>"
	},
	{
		"name": "<b>INGRESOS</b>"
	}]

	# Data Ingresos
	prepare_data = prepare_data_unpaid(filters)
	data.extend(prepare_data)

	# Agregar total de Ingresos
	total_unpaid = add_total_row(prepare_data, filters, True)
	data.extend(total_unpaid)

	# Data Egresos
	data.append({
		"name": "<b>EGRESOS</b>"
	})

	prepare_data_p = prepare_data_paid(filters)
	data.extend(prepare_data_p)

	# Agregar total de egresos
	total_paid = add_total_row(prepare_data_p, filters, False)
	data.extend(total_paid)

	# Agregar total, (Ingresos - Egresos)
	total_cash_flow = add_total_row_report(total_unpaid, total_paid, filters)
	data.extend(total_cash_flow)

	# Data para generar graficas
	chart = get_chart_data(columns)

	return columns, data, None, chart

@frappe.whitelist()
def get_payment_entries():
	'''Function that obtains the payment entries from the database'''
	# We get payment entries of payments received.
	payment_entry_received = frappe.db.sql("""SELECT posting_date, received_amount, paid_from_account_currency FROM `tabPayment Entry` WHERE payment_type = 'Receive'""", as_dict=True)
	# We get payment entries of payments made.
	payment_entry_paid = frappe.db.sql("""SELECT posting_date, paid_amount, paid_to_account_currency FROM `tabPayment Entry` WHERE payment_type = 'Pay'""", as_dict=True)
	write_file(payment_entry_received, 'develop_payment_entry_received')
	write_file(payment_entry_paid, 'develop_payment_entry_paid')
	return payment_entry_received, payment_entry_paid

def get_journal_entries():
	'''Function that obtains the payment entries from the database. Returns a list of dictionary objects.
	this function contains a write_file function that will write the results of its execution to a file. Comment it out when
	functionality has been confirmed.
	'''
	# Get journal entry accounts and amounts, for Cash and Bank transactions.
	journal_entry_accounts = frappe.db.sql("""SELECT parent, account_type, account, account_currency, debit_in_account_currency, credit_in_account_currency FROM `tabJournal Entry Account` WHERE account_type = 'Bank' OR account_type = 'Cash'""", as_dict=True)
	
	# For development and debugging: Save contents of data obtained to a file.
	write_file(journal_entry_accounts, 'develop_journal_entry_accounts')
	'''
	parent
	# To keep track of which journal entry is the parent, so date of journaling can be found.
	account_type
	# This is a crucial element. Any account which is not of Cash or Bank type, will be ignored!
	account
	# The account being used for the movement
	account_currency
	# The currency symbol for the accounting units for that specific journal entry account
	debit_in_account_currency
	# Debit in account currency units
	credit_in_account_currency
	# Credit in account currency units
	is_advance
	# Not immediately useful, but can be used for later segregation in report, so financial managers know which portion of the flows are advance payments (given or received)
	'''
	return journal_entry_accounts

def parse_journal_entry(journal_entry):
	'''[WIP] Function that obtains journal entry account data and segregates amounts received or paid'''
	# https://www.digitalocean.com/community/tutorials/how-to-handle-plain-text-files-in-python-3
	
	
	
	# for entry in journal_entry:
		#obtain dictionary object
		
		# read debit amount
		# read credit amount
		
		# if debit = 0, then bank or cash account is credited, which means money paid
		# if credit = 0, then bank or cash account is debited, which means money received.
		# should return a payment entry like object (so we can mix them seamlessly and then parse them!
	return journal_entry_results

def write_file(data_contents, filename):
	'''Function to write to a text file any data passed to the function, for debugging and development purposes only'''
	# https://www.digitalocean.com/community/tutorials/how-to-handle-plain-text-files-in-python-3
	file_path = '/home/alain/sihaysistema/apps/revelare/revelare/revelare/report/direct_cash_flow_report/' + str(filename) + '.txt'
	new_file = open(file_path,'w')
	contents = "The file now contains this text written from Python"
	new_file.write(str(data_contents))
	new_file.close()
	return

def get_columns(filters):
	'''Genera las columnas necesarias para el reporte'''

	columns = [{
		"fieldname": "name",
		"label": _("Direct Cash Flow"),
		"fieldtype": "Link",
		"options": "Budgeted Cash Flow",
		"width": 200
	}]
	# Obtains a list of pairs of datetime objects (start and end periods as per periodicity setting selected by user)
	ranges = get_period_date_ranges(filters)

	# Genera las columnas en base al rango de fechas
	for dummy, end_date in ranges:
		period = get_period(end_date, filters)

		columns.append({
			"label": _(period),
			"fieldname":scrub(period),
			"fieldtype": "Float",
			"width": 120
		})
		
	# TODO:  Sort the columns selected, at least for the weeks.

	return columns

def get_period_date_ranges(filters):
	'''Returns a list of a list of each periods start and end dates based on the initial and final dates. Each sublist
	is a datetime object with the start date for the period and end date for the period.'''
	# Relativedelta - for datetime calculations
	from dateutil.relativedelta import relativedelta
	from_date, to_date = getdate(filters.from_date), getdate(filters.to_date)
	
	# Get the value of the key passed to range. Then Setting the increment value according to the range
	increment = {
		"Monthly": 1,
		"Quarterly": 3,
		"Half-Yearly": 6,
		"Yearly": 12
	}.get(filters.range,1)

	# We create an empty list to hold the periodic date ranges, once filled up it will be returned.
	periodic_daterange = []
	# using range allows for specific amounts of looping. the first number is the start parameter:  1 (not 0). 53 is the ending value. Increment is the interval by which the loop should increment.  These are dummy variables.
	for dummy in range(1, 53, increment):
		if filters.range == "Weekly":
			# when entering the loop for the first time, from date contains user declared from date. On subsequent iterations, it is now the period end date + 1 day, so the new period of dates is calculated.  In this case, the next week.
			period_end_date = from_date + relativedelta(days=6)
		else:
			# when entering the loop for the first time, from date contains user declared "from date". On subsequent iterations, it is now the period end date + 1 day, so the new period of dates is calculated. In this case, the period end date is given the increment chosen above (1 month, 3 months, 6 months, 12 months).
			period_end_date = from_date + relativedelta(months=increment, days=-1)
			
		# If the period end date just estimated is greater than the to date (limit date chosen by user), the period end date is set to be the to date. This way, no date range is ever exceeded.
		if period_end_date > to_date:
			period_end_date = to_date
		# Having run all the checks, we finally append, to the list, another list with the from_date and the period end date.
		
		periodic_daterange.append([from_date, period_end_date])
		# this creates a new "from date" using the period end date just calculated and adding one day with relativedelta. This sets the stage for the next period.
		
		from_date = period_end_date + relativedelta(days=1)
		# if the period_end date just calculated ends up being 
		if period_end_date == to_date:
			break

	return periodic_daterange

def get_period(posting_date, filters):
	'''Returns the period based on the report filter'''

	months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

	if filters.range == 'Weekly':
		period = "Week " + str(posting_date.isocalendar()[1]) + " " + str(posting_date.year)
	elif filters.range == 'Monthly':
		period = str(months[posting_date.month - 1]) + " " + str(posting_date.year)
	elif filters.range == 'Quarterly':
		period = "Quarter " + str(((posting_date.month-1)//3)+1) +" " + str(posting_date.year)
	else:
		year = get_fiscal_year(posting_date, company=filters.company)
		period = str(year[2])

	return period

def prepare_data_unpaid(filters):
	'''Prepara la data en base a los registros pendientes por cobrar
		la estructura retornada sera un array con multiples diccionarios
		donde cada diccionario corresponde a una fila en el reporte
	'''

	data = []
	# Obtiene los items registrados pendientes por cobrar
	item_details = get_reg_unpaid(filters)
	ranges = get_period_date_ranges(filters)

	for item_data in item_details:

		row = frappe._dict({
			"name": _(item_data.party),
			"indent": flt(1)
		})

		total = 0
		for dummy, end_date in ranges:
			period = get_period(end_date, filters)
			fecha_registro = date_conversion(item_data.posting_date, filters)

			if fecha_registro == period:
				amount = flt(item_data.paid_amount)
				row[scrub(period)] = amount
				total += amount
			else:
				amount = 0.00
				row[scrub(period)] = amount
				total += amount

		row["total"] = total
		data.append(row)

	return data

def prepare_data_paid(filters):
	'''Prepara la data en base a los registros pagados (EGRESOS)
		la estructura retornada sera un array con multiples diccionarios
		donde cada diccionario corresponde a una fila en el reporte
	'''

	data = []
	# Obtiene los registros pagados (gastos)
	item_details = get_reg_paid(filters)
	# periodic_data = get_periodic_data(sle, filters)
	ranges = get_period_date_ranges(filters)

	for item_data in item_details:

		row = frappe._dict({
			"name": _(item_data.party),
			"indent": flt(1)
		})

		total = 0
		for dummy, end_date in ranges:
			period = get_period(end_date, filters)
			fecha_registro = date_conversion(item_data.posting_date, filters)

			# frappe.msgprint(_(period))
			if fecha_registro == period:
				amount = flt(item_data.paid_amount)
				row[scrub(period)] = amount
				total += amount
			else:
				amount = 0.00
				row[scrub(period)] = amount
				total += amount

		row["total"] = total
		data.append(row)

	return data

def get_chart_data(columns):
	'''retorna la data necesaria para mostrar las graficas en el reporte'''

	labels = [d.get("label") for d in columns[1:]]
	chart = {
		"data": {
			'labels': labels,
			'datasets':[]
		}
	}
	chart["type"] = "line"

	return chart

def get_reg_unpaid(filters):
	'''Returns the requested data from the database, in this case the records representing expected future receipts'''

	data_cash_flow = frappe.db.get_values('Budgeted Cash Flow',
										filters={'company': filters.get("company"), 'status_payment': 'Unpaid'},
										fieldname=['name', 'party', 'paid_amount', 'posting_date',
												'due_date'], as_dict=1)

	return data_cash_flow

def get_reg_paid(filters):
	'''Retorna la data solicitada de la base de datos, especificamente los registros
		pagados (EGRESOS)
	'''

	data_cash_flow = frappe.db.get_values('Budgeted Cash Flow',
										filters={'company': filters.get("company"), 'status_payment': 'Paid'},
										fieldname=['name', 'party', 'paid_amount', 'posting_date',
												'due_date'], as_dict=1)

	return data_cash_flow

def date_conversion(fecha, filters):
	'''Customized function to work with dates, especially weekly date ranges. TODO: Bimonthly (every 15 days), Daily'''
	'''Will not run if periodicity is monthly.'''
	if filters.range == 'Weekly':
		period = 'Week ' + str(fecha.isocalendar()[1]) + ' ' + str(fecha.year)
	elif filters.range == 'Monthly':
		period = fecha.strftime("%b %Y")
	elif filters.range == 'Quarterly':
		period = 'Quarter ' + str(((fecha.month - 1) //3) + 1) + ' ' + str(fecha.year)
	else:
		# period = str(fecha.year)
		year = get_fiscal_year(fecha, company=filters.company)
		period = str(year[2])
	
	write_file(period, 'develop_date_conversion_results')

	return period

def add_total_row(out, filters, tipo=False):
	'''Agrega el total de ingresos como egresos'''

	data = []

	if tipo:
		row_data = frappe._dict({
			"name": _("<b>Total Ingresos</b>")
		})

	else:
		row_data = frappe._dict({
			"name": _("<b>Total Egresos</b>")
		})

	ranges = get_period_date_ranges(filters)

	total = 0
	for row in out:
		for x in row:
			
			for dummy, end_date in ranges:
				period = get_period(end_date, filters)
				# frappe.msgprint(_(str(period.key)))
				if str(x.replace('_', ' ').capitalize()) == str(period):
					amount = (row[x])

					if str(x) != 'name':
						total += flt(amount)
						row_data.setdefault(scrub(period), 0.0)
						row_data[scrub((period))] += flt(amount)

				if filters.range == 'Yearly':
					if str(x) != 'name' and str(x) != 'indent' and str(x) != 'total':
						total += flt(row[scrub(period)])
						row_data.setdefault(scrub(period), 0.0)
						row_data[scrub((period))] += flt(row[scrub(period)])

	row_data["total"] = total
	data.append(row_data)
	data.append({})

	return data

def add_total_row_report(total_in, total_e, filters):
	'''Total del reporte resta la suma de ingresos con la suma de egresos'''

	data = []

	row_data = frappe._dict({
		"name": _("<b>Total Flujo de caja</b>")
	})

	for x in total_in:
		if x:
			total_ingresos = x
	
	for y in total_e:
		if y:
			total_egresos = y

	for item_ingreso in total_ingresos:
		for item_egreso in total_egresos:

			if item_egreso == item_ingreso:
				if item_egreso != 'name':
					row_data[str(item_egreso)] = float(total_ingresos[item_ingreso]
													 - total_egresos[item_egreso])

	data.append(row_data)
	data.append({})

	return data
