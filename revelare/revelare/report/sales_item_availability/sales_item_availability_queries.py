# Copyright (c) 2020, Si Hay Sistema and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, _dict, scrub


def item_availability_estimates_range(filters):
    """Function that returns the name of the submitted Item Availability Estimates
    that fall between the dates selected in the filter.

    Args:
        filters (dict): filters.from_date, filters.to_date, filters.company, filters.show_sales, filters.periodicty
    """
    result = frappe.db.sql(
        f"""
        SELECT name FROM `tabItem Availability Estimate` 
        WHERE docstatus=1 AND start_date AND end_date BETWEEN '{filters.from_date}' AND '{filters.to_date}'
        """, as_dict=True
    )
    return result

def periods_estimated_items(filters, parent):
    """Function that returns the code, amount, and amount uom of each estimated item
    belonging to a valid or submitted Item Availability Estimate

    Args:
        filters (dict): filters.from_date, filters.to_date, filters.company, filters.show_sales, filters.periodicty
        parent:  The parent of each one of these items, referring to Item Availability Estimate doctype
    Returns: A list of objects: [{'item_code': 'ITEMCODE-001', 'amount':'15.0', 'amount_uom': 'Pound'}]

    """
    result = frappe.db.sql(
        f"""
        SELECT item_code, amount, amount_uom FROM `tabEstimated Item` 
        WHERE docstatus=1 AND parent='{parent}';""", as_dict=True
    )
    return result

def estimation_item_attributes(filters, estimation_item_code):
    """Function that returns the estimation UOM, estimation name and stock_uom for use 
    in the calculations and in the report.

    Args:
        filters (dict): filters.from_date, filters.to_date, filters.company, filters.show_sales, filters.periodicty
        estimation_item_code:  The estimation item name, to find and obtain data from it.
    Returns: A list of dictionaries like this: 
    [{'name': 'CULTIVO-0069', 'estimation_name': 'Perejil', 'estimation_uom': 'Pound', 'stock_uom': 'Onza'}]
    """    
    result = frappe.db.sql(
        f"""
        SELECT name, estimation_name, estimation_uom, stock_uom FROM `tabItem` WHERE name='{estimation_item_code}';
        """, as_dict=True
    )
    return result

def find_bom_items(filters, estimation_item_code):
    """Function that returns the item_code, parent, stock_qty, stock_uom used in BOM Item, to prepare conversion for use 
    in the calculations, and to find BOM names that will help find Sales Items.

    Args:
        filters (dict): filters.from_date, filters.to_date, filters.company, filters.show_sales, filters.periodicty
        estimation_item_code:  The estimation item name, to find the BOM Items where it is listed, so that we may find the BOMs being used.
    """
    result = frappe.db.sql(
        f"""
        SELECT item_code, parent, stock_qty, stock_uom FROM `tabBOM Item` WHERE item_code='{estimation_item_code}';
        """, as_dict=True
    )
    return result

def find_boms(filters, bom):
    """Function that returns the item, quantity and uom to obtain from this bom, such that we may go find Sales Items.

    Args:
        filters (dict): filters.from_date, filters.to_date, filters.company, filters.show_sales, filters.periodicty
        bom:  The bom name or ID
    """
    result = frappe.db.sql(
        f"""
        SELECT item, quantity, uom FROM `tabBOM` WHERE name='{bom}';
        """, as_dict=True
    )
    return result

def find_sales_items(filters, item_code):
    """Function that returns the item code and item name for sales items only.

    Args:
        filters (dict): filters.from_date, filters.to_date, filters.company, filters.show_sales, filters.periodicty
        item_code: Item code for Item doctype
    """
    result = frappe.db.sql(
        f"""
        SELECT item_name, item_code FROM `tabItem` WHERE name='{item_code}' AND is_sales_item=1;
        """, as_dict=True
    )
    return result