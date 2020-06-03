# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,_
from odoo.exceptions import ValidationError


class Respartner(models.Model):

    _inherit = 'res.partner'

    is_pos_customer = fields.Boolean(string="Is Point of sales Customer",
                                     default=False)
    cid_number = fields.Char(string='CID Number', help="Identification Number")
    license_number = fields.Char(string="License Number")

    _sql_constraints = [
        ('license_number', 'unique(license_number)',
         'License Number must be unique !'),
        ('cid_number', 'unique(cid_number)',
         'CID Number must be unique !')
    ]

    @api.model
    def default_get(self, field_list):
        """ This method used to set Partner as Bhutan Country """
        res = super(Respartner, self).default_get(field_list)
        if 'country_id' in field_list:
            country_id = self.env['res.country'].search([('code', '=', 'BT')])
            if country_id:
                res.update({'country_id': country_id.id})
        return res

    @api.constrains('cid_number')
    def _check_cid_number(self):
        """Method to raise Validation for CID number less then 11 digits"""
        for rec in self:
            if rec.cid_number:
                if not rec.cid_number.isdigit():
                    raise ValidationError(_("Please enter digit value for "
                                            "CID Number !"))
                elif len(rec.cid_number) < 11:
                    raise ValidationError(_("Please enter CID Number as "
                                            "Eleven Digits !"))
                elif len(rec.cid_number) > 11:
                    raise ValidationError(_("CID Number should be only "
                                            "Eleven Digits !"))

    def unlink(self):
        """ Method to raise validation for
        unlink existing connection partner"""
        for rec in self:
            if rec.is_pos_customer:
                raise ValidationError(
                    _('You can not delete existing partner !!'))
        return super(Respartner, self).unlink()

