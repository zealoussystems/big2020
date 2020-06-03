# See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class AccountPayment(models.Model):
    """ Connection payment Reference"""

    _inherit = 'res.users'
    _description = 'Users'

    pos_config_ids = fields.Many2many('pos.config',
                                      string="Allowed Pos Seesion")

