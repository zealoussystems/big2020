from odoo import models, fields, api,_
from odoo.exceptions import ValidationError


class PosExtendedWizard(models. TransientModel):
    """Model for pos extended wizard."""

    _name = 'pos.extended.wizard'
    _description = 'Wizard to print Point of sales Report'

    start_date = fields.Datetime('Start Date',
                                 default=fields.Datetime.now)
    end_date = fields.Datetime('End Date')
    partner_id = fields.Many2one('res.partner', string='Customer')
    is_lpg = fields.Boolean('Is Customer Copy ?', default=True,
                            help="Display only LPG Product")

    def print_report(self):
        """Print report method."""
        if(self.start_date and self.end_date and
                self.start_date > self.end_date):
            raise ValidationError(_("Start date should be "
                                    "greater than end date !!"))
        else:
            domain = [
                ('order_id.date_order', '>=', self.start_date),
                ('order_id.date_order', '<=', self.end_date),
                ('order_id.partner_id', '=', self.partner_id.id)]
            if self.is_lpg:
                domain.append(('product_id.is_refile_lpg_product', '=', True))
            pos_order_line_ids = self.env['pos.order.line'].search(domain)
            if not pos_order_line_ids:
                raise ValidationError(_("Record not Found !! "))
            return self.env.ref(
                'big_pos_extended.action_pos_extended_report'
            ).report_action(self)