from odoo import fields, models


class ProductTemplate(models.Model):
    """Inherited Model product template."""

    _inherit = "product.template"

    purchase_request = fields.Boolean(
        help="Check this box to generate Purchase Request instead of "
             "generating Requests For Quotation from procurement."
    )
