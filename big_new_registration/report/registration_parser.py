import pytz
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import api, models,_


class RegistrationParserReport(models.AbstractModel):
    """Registration parser report."""

    _name = "report.big_new_registration.new_registration"
    _description = "New Connection Report Details"

    def _get_detail(self, start_date, end_date):
        """Method to get report registration details."""
        data_list = []
        registration_ids = self.env['connection.history'].search([
            ('type', 'in', ['New Connection', 'Additional Connection']),
            ('date', '>=', start_date),
            ('date', '<=', end_date),
            ('new_connection_id.state', '=', 'done')], order="id desc")
        for rec in registration_ids:
            data_dict = {'number': rec.new_connection_id.number,
                         'date': rec.date,
                         'type': rec.type,
                         'partner_id':
                             rec.new_connection_id.partner_id and
                            rec.new_connection_id.partner_id.name or '',
                         'license_number':
                             rec.new_connection_id.license_number,
                         'money_receipt_no': rec.money_receipt_no,
                         'cylinder_qty': rec.qty,
                         'security_deposit_amount':
                             rec.security_deposit_amount,
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
        registration = self.env[
            'ir.actions.report']._get_report_from_name(
            'big_new_registration.new_registration')
        return {'doc_ids': docids,
                'doc_model': registration.model,
                'data': data,
                'docs': self.env['registration.wizard'].browse(docids),
                'get_detail': self._get_detail,
                'get_datatime': self._get_datatime,
                }
