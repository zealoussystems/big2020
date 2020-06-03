# See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _


class PosOrder(models.Model):
    """ Point of sales"""

    _inherit = 'pos.order'
    _description = 'Point of sales'

    new_connection_id = fields.Many2one('new.registration.process',
                                        string="Registration Number")
    is_new_connection = fields.Boolean(string="Is New Connection ?")

    def create_picking_for_empty_cylinder(self):
        """Create a picking for each order and validate it."""
        Picking = self.env['stock.picking']
        # If no email is set on the user, t
        # he picking creation and validation will fail be cause of
        # the 'Unable to log message,
        # please configure the sender's email address.' error.
        # We disable the tracking in this case.
        if not self.env.user.partner_id.email:
            Picking = Picking.with_context(tracking_disable=True)
        Move = self.env['stock.move']
        StockWarehouse = self.env['stock.warehouse']
        for order in self:
            if not order.lines.filtered(
                    lambda l: l.product_id.type in ['product', 'consu']):
                continue
            address = order.partner_id.address_get(['delivery']) or {}

            picking_type = order.picking_type_id.return_picking_type_id or \
                           order.picking_type_id
            order_picking = Picking
            return_picking = Picking
            moves = Move
            destination_id = picking_type.default_location_src_id.id
            if order.partner_id:
                location_id = order.partner_id.property_stock_customer.id
            else:
                if (not picking_type) or (
                not picking_type.default_location_dest_id):
                    customerloc, supplierloc = \
                        StockWarehouse._get_partner_locations()
                    location_id = customerloc.id
                else:
                    location_id = picking_type.default_location_dest_id.id
            if picking_type:
                message = _(
                    "This transfer has been created from "
                    "the point of sale session: "
                    "<a href=# data-oe-model"
                    "=pos.order data-oe-id=%d>%s</a>") % (
                          order.id, order.name)
                picking_vals = {
                    'origin': order.name,
                    'partner_id': address.get('delivery', False),
                    'user_id': False,
                    'date_done': order.date_order,
                    'picking_type_id': picking_type.id,
                    'company_id': order.company_id.id,
                    'move_type': 'direct',
                    'note': order.note or "",
                    'location_id': location_id,
                    'location_dest_id': destination_id,
                }
                pos_qty = any([x.qty > 0 for x in order.lines if
                               x.product_id.type in ['product', 'consu']])
                if pos_qty:
                    order_picking = Picking.create(picking_vals.copy())
                    if self.env.user.partner_id.email:
                        order_picking.message_post(body=message)
                    else:
                        order_picking.sudo().message_post(body=message)

            product_id = self.env['product.product'].search(
                [('is_empty_cylinder_product', '=', True)], limit=1)

            pos_qty = sum([x.qty for x in order.lines if
                           x.product_id.type in ['product', 'consu'] and
                           x.product_id.is_refile_lpg_product])
            if pos_qty:
                moves |= Move.create({
                    'name': product_id.name,
                    'product_uom': product_id.uom_id.id,
                    'picking_id': order_picking.id,
                    'picking_type_id': picking_type.id,
                    'product_id': product_id.id,
                    'product_uom_qty': abs(pos_qty),
                    'state': 'draft',
                    'location_id': location_id,
                    'location_dest_id': destination_id,
                })
            if order_picking:
                order._force_picking_done(order_picking)
        return True

    def create_picking(self):
        """" Method inherit to call empty cylinder qty"""
        res = super(PosOrder, self).create_picking()
        for order in self:
            if not order.is_new_connection:
                order.create_picking_for_empty_cylinder()
            else:
                new_connection_id = \
                    self.env['new.registration.process'].search([
                        ('partner_id', '=', order.partner_id.id),
                        ('state', '=', 'done')], limit=1)
                order.new_connection_id = new_connection_id \
                                          and new_connection_id.id
        return res

    @api.model
    def _order_fields(self, ui_order):
        res =super(PosOrder, self)._order_fields(ui_order)
        res['is_new_connection'] = ui_order.get('is_new_connection', False)
        return res

class NewRegistrationProcess(models.Model):
    """ Registration Process"""

    _inherit = 'new.registration.process'
    _description = 'New Registration Process'

    @api.depends('cylinder_qty', 'pos_order_ids',
                 'connection_history_ids.state')
    def _compute_remaining_qty(self):
        """ Calculate remaining qty to deliver """
        for rec in self:
            pos_qty = 0.0
            connection_qty = sum([x.qty for x in rec.connection_history_ids
                                  if x.type in [
                                      'New Connection',
                                      'Additional Connection'] and
                                  x.state == 'done'])
            if rec.pos_order_ids:
                for pos_line in rec.pos_order_ids:
                    pos_qty += sum(x.qty for x in pos_line.lines
                                   if x.product_id.is_refile_lpg_product)
            rec.remaining_qty_deliver = (connection_qty - pos_qty)

    pos_order_ids = fields.One2many('pos.order','new_connection_id',
                                    string="Pos Orders")
    remaining_qty_deliver = fields.Integer(
        compute='_compute_remaining_qty',
        string="Remaining Cylinder Qty to Deliver", store=True)

class ResPartner(models.Model):
    """ Res partner class extended """
    _inherit='res.partner'

    @api.depends('new_registration_ids.remaining_qty_deliver',
                 'new_registration_ids.cylinder_qty',
                 'new_registration_ids.state')
    def _compute_remaining_qty(self):
        """ Compute remaining deliver qty and total register qty"""
        for rec in self:
            rec.remaining_qty = \
                sum([x.remaining_qty_deliver for x
                     in rec.new_registration_ids])
            rec.register_qty = \
                sum([x.cylinder_qty for x in rec.new_registration_ids
                     if x.state == 'done'])

    new_registration_ids = fields.One2many(
        'new.registration.process', 'partner_id',
        string="New Registration Orders")
    register_qty = fields.Integer(compute='_compute_remaining_qty', store=True,
                                  string="Register Qty")
    remaining_qty = fields.Integer(string="Remaining Qty to Deliver")