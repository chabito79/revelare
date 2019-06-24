// Copyright (c) 2016, SHS and contributors
// For license information, please see license.txt
/* eslint-disable */

// Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.require("assets/erpnext/js/financial_statements.js", function() {
	frappe.query_reports["Improved Cash Flow"] = $.extend({},
		erpnext.financial_statements);
	
	// The last item in the array is the definition for Presentation Currency
	// filter. It won't be used in cash flow for now so we pop it. Please take
	// of this if you are working here.
	frappe.query_reports["Improved Cash Flow"]["filters"].pop();

	// Finds the array position of the periodicity filter object so it can be spliced or removed.
	const remove_position = frappe.query_reports["Improved Cash Flow"]["filters"].indexOf(frappe.query_reports["Improved Cash Flow"]["filters"].find(fruit => fruit.fieldname === 'periodicity'))
	// Removes the periodicity filter object to prepare for replacement with Monthly default.
	frappe.query_reports["Improved Cash Flow"]["filters"].splice(remove_position,1);
	
	// We add filters to the array. In this case we add back the periodicity filter, which is crucial, but this time the dafult is monthly.
	frappe.query_reports["Improved Cash Flow"]["filters"].push(
	{
		"fieldname": "periodicity",
		"label": __("Periodicity"),
		"fieldtype": "Select",
		"options": [
			{ "value": "Monthly", "label": __("Monthly") },
			{ "value": "Quarterly", "label": __("Quarterly") },
			{ "value": "Half-Yearly", "label": __("Half-Yearly") },
			{ "value": "Yearly", "label": __("Yearly") }
		],
		"default": "Monthly",
		"reqd": 1
	},
	{
		"fieldname": "accumulated_values",
		"label": __("Accumulated Values"),
		"fieldtype": "Check"
	});
});

