# See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class ConnectionHistory(models.Model):
    """ This class create for New connectiona and additional connectiona and
    Surrendered process history records."""

    _name = 'connection.history'
    _rec_name = 'money_receipt_no'
    _description = 'Connection History'

    date = fields.Datetime(string="Date and time",
                           default=fields.Datetime.now)
    new_connection_id = fields.Many2one('new.registration.process',
                                        string="New Connection Reference")
    additional_connection_id = fields.Many2one('additional.connection',
                                               string="Additional Connection")
    qty = fields.Integer(string="Cylinder Qty")
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
    money_receipt_no = fields.Char(string='Money Receipt No')
    type = fields.Char(string="Connection Type")
    is_cancel_qty = fields.Boolean(string="Is all Cancel Qty")
    payment_mode = fields.Selection([('cash', 'Cash'), ('cheque', 'Cheque')],
                                    string="Payment Type")
    cheque_no = fields.Char(string="Cheque Number")
    cheque_date = fields.Date(string="Cheque Date")
    state = fields.Selection([('confirm', 'Approved by Sales Point'),
                              ('done', 'Approved by BIG'),
                              ('reject', 'Reject'),
                              ('cancel', 'Cancel')], default='confirm')

    def get_amount(self, amount):
        """ Method to convert amount in Words"""
        amt_en = self.currency_id.amount_to_text(amount)
        return amt_en

    def print_payment_receipt_report(self):
        """Method to pront Payment receipt report"""
        return {
            'type': 'ir.actions.report',
            'report_name': 'big_new_registration.report_payment_receipt',
            'model': 'connection.history',
            'report_type': "qweb-pdf",
        }