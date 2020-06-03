# See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class BigSecurityConfiguration(models.Model):

    _name = 'security.config'
    _description = 'Security Deposit Configuration'
    _rec_name = 'company_id'

    start_date = fields.Date(string='Start Date', required=True,
                           help="Security Deposit Start Date and Time")
    end_date = fields.Date(string='End Date', required=True,
                           help="Security Deposit End Date and Time")
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company',
        default=lambda self: self.env.user.company_id,
        help="Company of logged in user")
    currency_id = fields.Many2one(
        comodel_name='res.currency', string='Currency',
        default=lambda self: self.env.user.company_id.currency_id)
    security_deposit_amount = fields.Monetary(
        currency_field='currency_id',
        string="Security Deposit Amount",
        help="Total Security Deposit Amounts")
    user_id = fields.Many2one('res.users', string="Responsible",
                              default=lambda self: self.env.user,
                              help="Current User")


