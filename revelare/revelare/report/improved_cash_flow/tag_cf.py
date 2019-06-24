from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint

# esta funcion obtiene las cuentas que tengan el tag correspondiente
# Inicialmente la funcion debe jalar todas aquellas que tengan "CF-" al inicio.
def get_tag_based_gl_data(company, start_date, end_date, _user_tags):
	gl_sum = frappe.db.sql_list("""
		select sum(credit) - sum(debit)
		from `tabGL Entry`
		where company=%s and posting_date >= %s and posting_date <= %s
			and voucher_type != 'Period Closing Voucher'
			and account in ( SELECT name FROM tabAccount WHERE _user_tags = %s)
	""", (company, start_date, end_date, _user_tags))
    # Esta función ya hace un filtrado y retorna 0 si no hay algo.
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


# Obtener las categorias de Cash Flow basado en los tags
# Se obtiene un 

def get_cash_flow_accounts():
	operation_accounts = {
		"section_name": "Operations",
		"section_footer": _("Net Cash from Operations"),
		"section_header": _("Cash Flow from Operations"),
		"account_types": [
			# 
			{"account_type": "Depreciation", "label": _("Depreciation")},
			{"account_type": "Receivable", "label": _("Net Change in Accounts Receivable")},
			{"account_type": "Payable", "label": _("Net Change in Accounts Payable")},
			{"account_type": "Stock", "label": _("Net Change in Inventory")}
			# 			{"account_type": "Income Tax", "label": _("Net Change in Income Tax")}
			# 			{"account_type": "Sales Tax", "label": _("Net Change in Sales Tax")}
		]
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
# Jalan la data del gl entry de aquellas cuentas que posean el CF al python.
# Dividimos los resultados en cuentas que vayan a OP-erating  a IN-vestment  y a FI-nancing
# Ya divididos, ahora se calcula la diferencia y/o suma de aquellas cuentas que posean la MISMA categoria.
# se suman todas las que posean la misma categoria, pero sean de tipo pasivo o equity y luego las de activo, calculando la diferencia
# finalmente se estrucutra la data para pasar al informe
