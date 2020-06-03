import pytz
from odoo import api, models
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class PosReportParser(models.AbstractModel):

    _name = "report.big_pos_extended.customer_details"
    _description='Point of sales report'

    def get_partner_details(self, start_date, end_date, partner, is_lpg):
        """ Get details with partner sales"""
        data_list = []
        domain = [
            ('order_id.date_order', '>=', start_date),
            ('order_id.date_order', '<=', end_date),
            ('order_id.partner_id', '=', partner.id),
        ]
        if is_lpg:
            domain.append(('product_id.is_refile_lpg_product', '=', True))
        pos_order_line_ids = self.env['pos.order.line'].search(domain)
        for rec in pos_order_line_ids:
            data_dict = {'name': rec.order_id.name,
                         'date_order': rec.order_id.date_order,
                         'partner_id': rec.order_id.partner_id and
                                       rec.order_id.partner_id.name or '',
                         'product_id': rec.product_id and
                                       rec.product_id.name or '',
                         'qty': rec.qty,
                         'price_unit': rec.price_unit,
                         'price_subtotal_incl': rec.price_subtotal_incl,
                         }
            data_list.append(data_dict)
        return data_list

    def _get_datatime(self, date):
        """Method to convert time as per user timezone"""
        user = self.env.user
        local_tz = pytz.timezone(user.tz or 'UTC')
        display_date = date and datetime.strftime(pytz.utc.localize(
            datetime.strptime(str(date),
                              DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(
            local_tz), "%d/%m/%Y %H:%M:%S") or ''
        return display_date

    @api.model
    def _get_report_values(self, docids, data=None):
        """Method to get report values."""
        pos_order = self.env[
            'ir.actions.report']._get_report_from_name(
            'big_pos_extended.customer_details')
        return {'doc_ids': docids,
                'doc_model': pos_order.model,
                'data': data,
                'docs': self.env['pos.extended.wizard'].browse(docids),
                'get_partner_details': self.get_partner_details,
                'get_datatime': self._get_datatime,
                }




