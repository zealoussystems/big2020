from odoo import fields, models
from odoo.exceptions import ValidationError


class BigCancelRegWizard(models.TransientModel):
    """ Wizard for cancel connection Report"""

    _name = "big.cancel.wizard"
    _description = "wizard for cancel connection report."

    start_date = fields.Datetime('Start Date', default=fields.Datetime.now,
                                 help="Start date")
    end_date = fields.Datetime('End Date', default=fields.Datetime.now,
                               help="End date")
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company',
        default=lambda self: self.env.user.company_id,
        help="Company of logged in user")

    def print_report(self):
        """Method to print report."""
        if (self.start_date and self.end_date and
                self.start_date > self.end_date):
            raise ValidationError(('''Start Date should be greater than
            End date!'''))
        else:
            return self.env.ref(
                'big_new_registration.action_cancel_connection_report'
            ).report_action(self)
