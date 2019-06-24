from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint

def data_query():
	queryOP = frappe.db.sql("SELECT account_name, _user_tags FROM tabAccount WHERE _user_tags LIKE '%CF-OP-%'",as_dict=1)
	queryIN = frappe.db.sql("SELECT account_name, _user_tags FROM tabAccount WHERE _user_tags LIKE '%CF-IN-%'",as_dict=1)
	queryFI = frappe.db.sql("SELECT account_name, _user_tags FROM tabAccount WHERE _user_tags LIKE '%CF-FI-%'",as_dict=1)

	row_names_OP = []
	row_names_IN = []
	row_names_FI = []
	for each in queryOP:
		tag_list = each["_user_tags"].split("-")
		row_names_OP.append(tag_list[2])
	for each in queryIN:
		tag_list = each["_user_tags"].split("-")
		row_names_IN.append(tag_list[2])
	for each in queryIN:
		tag_list = each["_user_tags"].split("-")
		row_names_FI.append(tag_list[2])
	
	unique_OP = list(set(row_names_OP))
	unique_IN = list(set(row_names_IN))
	unique_FI = list(set(row_names_FI))
	
	# unique = { str(each['name']) : each for each in data_com_uno }.values()
	
	return unique_OP, unique_IN, unique_FI # row_names_OP, row_names_IN, row_names_FI #queryOP, queryIN, queryFI

# esta funcion obtiene las cuentas que tengan el tag correspondiente
# Inicialmente la funcion debe jalar todas aquellas que tengan "CF-" al inicio.
def get_tag_based_gl_data(company, start_date, end_date, _user_tags):
	gl_sum = frappe.db.sql_list("""
		select sum(credit) - sum(debit)
		from `tabGL Entry`
		where company=%s and posting_date >= %s and posting_date <= %s
			and voucher_type != 'Period Closing Voucher'
			and account in ( SELECT name FROM tabAccount LIKE _user_tags = %s)
	""", (company, start_date, end_date, _user_tags))
	# Esta funcion ya hace un filtrado y retorna 0 si no hay algo.
	return gl_sum[0] if gl_sum and gl_sum[0] else 0

def get_tag_based_data(company, user_tags, period_list, accumulated_values):
	data = {}
	total = 0
	for period in period_list:
		start_date = get_start_date(period, accumulated_values, company)

		amount = get_tag_based_gl_data(company, start_date, period['to_date'], user_tags)
		if amount and account_type == "Depreciation":
			amount *= -1
		
		total += amount
		data.setdefault(period["key"], amount)

	data["total"] = total
	return data

def account_types(unique_account_list):
	"""crea diccionario con nombres de filas unicos"""
	list_of_dict = []
	for each in unique_account_list:
		# create the dict
		thisdict =	{}
		thisdict["account_type"] = each
		thisdict["label"] = _(each)

		# append to list_of dict
		list_of_dict.append(thisdict)
	# list_of_dict = [
	# 	{"account_type": "Parangaricutirimicuaro", "label": _("Depre")},
	# 	{"account_type": "Receivable", "label": _("Net Change in Accounts Receivable")},
	# 	{"account_type": "Payable", "label": _("Net Change in Accounts Payable")},
	# 	{"account_type": "Stock", "label": _("Net Change in Inventory")}
	# ]
	return list_of_dict #list de diccionarios con N accounts para cada N rows


# Obtener las categorias de Cash Flow basado en los tags
# Se obtiene un
def get_cash_flow_accounts(unique_OP, unique_IN, unique_FI):

	## ([[u'Depreciacion Palito', u',CF-OP-Depreciation-A'], [u'Depreciaciones', u',CF-OP-Depreciation-A']], [], [])
	operation_accounts = {
		"section_name": "Operations",
		"section_footer": _("Net Cash from Operations"),
		"section_header": _("Cash Flow from Operations"),
		# Account types, generate a list with objects where Account Type = unique user taf and label = unique user tag,
		"account_types": account_types(unique_OP)
	}

	investing_accounts = {
		"section_name": "Investing",
		"section_footer": _("Net Cash from Investing"),
		"section_header": _("Cash Flow from Investing"),
		"account_types": [
			{"account_type": "Fixed Asset", "label": _("Net Change in Fixed Asset")}
		]
	}

	financing_accounts = {
		"section_name": "Financing",
		"section_footer": _("Net Cash from Financing"),
		"section_header": _("Cash Flow from Financing"),
		"account_types": [
			{"account_type": "Equity", "label": _("Net Change in Equity")}
		]
	}

	# combine all cash flow accounts for iteration
	return [operation_accounts, investing_accounts, financing_accounts]

# Seleccionar SOLO aquellos tags que empiezen con CF
# Buscar cuentas
# Definir categorias.
# Jalan la data del gl entry de aquellas cuentas que posean el CF al python.
# Dividimos los resultados en cuentas que vayan a OP-erating  a IN-vestment  y a FI-nancing
# Ya divididos, ahora se calcula la diferencia y/o suma de aquellas cuentas que posean la MISMA categoria.
# se suman todas las que posean la misma categoria, pero sean de tipo pasivo o equity y luego las de activo, calculando la diferencia
# finalmente se estrucutra la data para pasar al informe
