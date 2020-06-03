# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class StockPicking(models.Model):
    """ Inherit object to added vehical and driver name fields"""
    _inherit = 'stock.picking'

    vehical_no = fields.Char(string="Vehical Number",
                             help="Transportation Vehical Number")
    driver_name = fields.Char(string="Driver Name",
                              help="Transportation Driver name")
    is_new_picking = fields.Boolean(string="Is New Product Picking",
                                    defualt=False)
    transfer_picking_id = fields.Many2one(comodel_name='stock.picking',
                                          string="Transfer From",
                                          domain=[('state', '=', 'done')])
    picking_type_code = fields.Selection(related='picking_type_id.code',
                                       string="Picking Code")

    def create_new_sequence(self):
        """ Added sequence based on New Product"""
        for rec in self:
            if not rec.is_new_picking:
                rec.name = str("NEW/" + rec.name)
                rec.is_new_picking = True

    def reset_new_product(self):
        """ Reset sequence based on New Product"""
        for rec in self:
            if rec.is_new_picking:
                rec.name = rec.name[4:]
                rec.is_new_picking = False

    @api.onchange('transfer_picking_id')
    def onchange_transfer_picking_id(self):
        """ Onchange method to set value of Transfer move liens,
        vehical number and driver details for Internal Transfer"""
        for rec in self:
            transfer_picking_list = []
            if rec.transfer_picking_id:
                rec.vehical_no = rec.transfer_picking_id.vehical_no
                rec.driver_name = rec.transfer_picking_id.driver_name
                rec.location_id = rec.transfer_picking_id.location_dest_id.id
                rec.location_dest_id = False
                for line in rec.transfer_picking_id.move_ids_without_package:
                    transfer_move_line_vals = (0, 0, {
                        'name': line.name,
                        'date': line.date,
                        'location_dest_id': rec.location_dest_id and
                                            rec.location_dest_id.id or False,
                        'location_id': rec.location_id and
                                       rec.location_id.id or False,
                        'product_id': line.product_id
                                      and line.product_id.id or False,
                        'product_uom': line.product_uom
                                       and line.product_uom.id or False,
                        'quantity_done': line.quantity_done or 0.0,
                        'product_uom_qty': line.product_uom_qty or 0.0,
                        'company_id': line.company_id.id,
                    })
                    transfer_picking_list.append(transfer_move_line_vals)
                rec.move_ids_without_package = transfer_picking_list
            else:
                rec.vehical_no = rec.driver_name = ''
                rec.move_ids_without_package = False
                rec.location_id = False
                rec.location_dest_id = False

class StockMove(models.Model):
    """ Inherit object to added account move reference and create invoice"""
    _inherit = 'stock.move'

    @api.depends('product_id', 'quantity_done')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = rec.product_id.lst_price * rec.quantity_done

    account_move_id = fields.Many2one(comodel_name='account.move',
                                      string="Invoice Reference")
    amount_total = fields.Float(string="Total Amount", store=True,
                                compute="_compute_amount_total")
    is_invoice = fields.Boolean(string="Is Invoice Create")

    def create_invoice(self):
        """ This method used to create invoice from picking based on
            picking move lines """
        account_move_obj = self.env['account.move']
        for move_line in self:
            if move_line.product_id:
                move_vals = {'partner_id': self.picking_id.partner_id.id,
                             'type': 'in_invoice',
                             'invoice_line_ids': [(0, 0, {
                                'product_id': move_line.product_id.id,
                                'quantity': move_line.quantity_done,
                                'price_unit': move_line.product_id.lst_price,
                                'name': move_line.name,
                             })],
                             }
                account_move_id = account_move_obj.create(move_vals)
                move_line.account_move_id = account_move_id.id
                move_line.is_invoice = True
