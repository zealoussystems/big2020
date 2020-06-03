import pytz
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import api, models


class CancelConnectionParserReport(models.AbstractModel):
    """Cancel connection parser report."""

    _name = "report.big_new_registration.cancel_connection"
    _description = "Cancel Connection Report Details"

    def _get_detail(self, start_date, end_date):
        """Method to get report cancel connection details."""
        data_list = []
        cancel_connection_ids = self.env['cancel.connection'].search([
            ('state', '=', 'cancel_big'), ('date', '>=', start_date),
            ('date', '<=', end_date)])
        for rec in cancel_connection_ids:
            data_dict = {'new_connection_id': rec.new_connection_id and
                         rec.new_connection_id.number or '',
                         'date': rec.date,
                         'partner_id': rec.partner_id and
                         rec.partner_id.name or '',
                         'license_number': rec.license_number,
                         'money_receipt_no': rec.money_receipt_no,
                         'cylinder_qty': rec.cylinder_qty,
                         'security_deposit_amount':
                             rec.security_deposit_amount
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
        registration = self.env['ir.actions.report']._get_report_from_name(
            'big_new_registration.cancel_connection')
        return {'doc_ids': docids,
                'doc_model': registration.model,
                'data': data,
                'docs': self.env['big.cancel.wizard'].browse(docids),
                'get_detail': self._get_detail,
                'get_datatime': self._get_datatime,
                }
