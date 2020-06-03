# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    is_approved = fields.Boolean("Is Approved by Manager", copy=False)
    purchase_id = fields.Many2one('purchase.order', string="Purchase Order")
    po_amount = fields.Monetary(related='purchase_id.amount_total',
        string='Purchase Amount', currency_field='currency_id')

    def approve_ceo(self):
        '''Method to approve supplier payment by the
        company's director'''
        for rec in self:
            rec.is_approved = True

    def post(self):
        '''Override method to raise validations.'''
        res = super(AccountPayment, self).post()
        account_move = self.env['account.move'].browse(
            self._context.get('active_id'))
        for rec in self:
            if (account_move and account_move.type in
                    ['in_invoice', 'in_refund'] and account_move.is_approved):
                rec.is_approved = True

            if (rec.payment_type in ['outbound', 'transfer']
                    and not rec.is_approved):
                raise ValidationError(_("You cannot make payment "
                                        "because it is not approved by "
                                        "CEO !!"))
        return res

    def action_draft(self):
        """ Inherit method for false approve fields"""
        res = super(AccountPayment, self).action_draft()
        for rec in self:
            if rec.is_approved:
                rec.is_approved = False
        return res

    @api.onchange('partner_id', 'partner_type', 'payment_type')
    def onchange_partner_id(self):
        """ Onchange of Partner po order false"""
        for rec in self:
            if not rec.partner_id or rec.payment_type != 'outbound' or \
                    rec.partner_type:
                rec.purchase_id = False

