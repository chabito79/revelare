# -*- coding: utf-8 -*-
#  Si Hay Sistema and Contributors 2020
from __future__ import unicode_literals
from . import __version__ as app_version

"""
en-US: Make sure all fields that are coming from another branch and the new fields you require are added to the fixtures
list.
es-GT: Asegurate que todos los fixtures que vengan de otra rama y los
nuevos fixtures que estes creando se agreguen al listado fixtures.

"""


def fill_fixtures():
    # We declare fixtures as an empty list.
    fixtures_fillup = []

    # Add the corresponding fields to the fixture objects
    # if the object does not exist, simply create it and copy accordingly.

    custom_field = {
        "dt": "Custom Field", "filters": [
            [
                "name", "in", [
                    "Item-availability_estimates",
                    "Item-include_in_estimations",
                    "Item-column_break_estimations",
                    "Item-estimation_uom",
                    "Item-estimation_name"
                ]
            ]
        ]
    }

    translation = {
        "dt": "Translation", "filters": [
            [
                "source_name", "in", [
                    "Amount UOM",
                    "Estimated Items and Quantities Available",
                    "Estimated Available Items",
                    "Availability Estimates",
                    "Estimation Name",
                    "Item Availability Estimate Importer",
                    "Include in Estimations",
                    "Estimation UOM",
                    "REVELARE: Only for Items used as materials in Bill of Materials (BOM) or Items marked for sale If checked, Item will be included automatically in the Sales Item Availability Report.",
                    "REVELARE: Default Unit of Measure to be used in Item Availability Estimates. Applies only to Material Items, not for Sales Items.",
                    "REVELARE: Name to be displayed as a header for Sales Item groupings used in Sales Item Availability Report.",
                    "Sales Item Availability",
                    "Show sales adjustments",
                    "Obtain sales adjustments from",
                    "Item Availability Estimate",
                    "Valid from this date",
                    "Until this date",
                    "Estimate Validity Interval",
                    "Days",
                    "Interval duration in days",
                    "Code",
                    "Name",
                    "Possible",
                    "UOM",
                    "Sold",
                    "Available",
                    "Revelare Configuration",
                    "Configuration",
                    "Pound",
                    "Sales Estimates"
                ]
            ]
        ]
    }

    tax_category = {
        "dt": "Tax Category", "filters": [
            [
                "title", "in", [
                    "SAT: Entidad Publica",
                    "SAT: Exportador"
                ]
            ]
        ]
    }

    id_doctype = {
        "dt": "Identification Document Type", "filters": [
            [
                "identification_document_type", "in", [
                    "PAS"
                ]
            ]
        ]
    }

    # NEW FUNCTIONALITY FOR EXPORTING
    fixtures_fillup.append(custom_field)
    fixtures_fillup.append(translation)
    # fixtures_fillup.append(tax_category)
    # fixtures_fillup.append(id_doctype)

    return fixtures_fillup

# fixtures = fill_fixtures()
