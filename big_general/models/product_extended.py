# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,_


class ProductProduct(models.Model):

    _inherit = 'product.product'

    is_empty_cylinder_product = fields.Boolean(
        string='Is Empty Cylinder', help="Empty cylinder Product")
    is_refile_lpg_product = fields.Boolean(
        string='Is Refile LPG', help="Refile LPG cylinder Product")
