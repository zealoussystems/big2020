# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,_


class ResCompany(models.Model):

    _inherit = 'res.company'

    tpn_number = fields.Char(string='TPN Number',
                             help="TPN Identification Number")
    security_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Security Deposit Account',
        help='Security Deposit Account')
