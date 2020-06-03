# See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    """ Connection payment Reference"""

    _inherit = 'account.payment'
    _description = 'Account Payments'

    new_connection_id = fields.Many2one('new.registration.process',
                                        string="New Conection Reference")
    history_connection_id = fields.Many2one('connection.history',
                                            string="History Connection "
                                                   "Reference")

    @api.depends('invoice_ids', 'payment_type', 'partner_type', 'partner_id')
    def _compute_destination_account_id(self):
        """ Method to set security deposit account in payments"""
        res = super(AccountPayment, self)._compute_destination_account_id()
        if self.env.context.get('security_deposit', False) \
                or self.new_connection_id:
            if self.company_id.security_account_id:
                self.destination_account_id = \
                    self.company_id.security_account_id.id or False
            else:
                raise ValidationError(_("Please Configure Security Deposit"
                                        "account in Company !!"))
        return res
