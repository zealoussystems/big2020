# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,_


class ResUsers(models.Model):

    _inherit = 'res.users'

    warehouse_id = fields.Many2one(comodel_name='stock.warehouse',
                                         string="Warehouse")
    stock_location_id = fields.Many2one(comodel_name='stock.location',
                                        string="Stock Location",
                                        help = "Stock Dzongkhag")
    customer_damage_location_id = fields.Many2one(comodel_name='stock.location',
                                        string="Customer Damage Location",
                                        help = "Customer Damage Location")
    location_ids = fields.Many2many('stock.location',
                                    string="Multiple Stock Locations")

