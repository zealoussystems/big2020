# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    """ Inherit object to added fields for approvenments"""

    _inherit = 'account.move'

    is_approved = fields.Boolean("Is Approved by Manager", copy=False)

    def approve_state(self):
        '''Method to approve supplier invoice by the
        company's director'''
        for rec in self:
            if rec.type in ['in_invoice', 'in_refund']:
                rec.is_approved = True

    def action_invoice_register_payment(self):
        ''' Override method to raise validations. '''
        if self.type in ['in_invoice', 'in_refund'] and not self.is_approved:
                raise ValidationError(_("You cannot make payment "
                                        "because it is not approved by "
                                        "CEO !!"))
        return super(AccountMove, self).action_invoice_register_payment()

    def button_draft(self):
        """ Inherit metod for false approve fields"""
        res = super(AccountMove, self).button_draft()
        for rec in self:
            if rec.is_approved:
                rec.is_approved = False
        return res
