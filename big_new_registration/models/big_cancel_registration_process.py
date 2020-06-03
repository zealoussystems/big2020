# See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class CancelConnection(models.Model):
    """ This Class create for Cancel Process of Existing Customer connection"""

    _name = 'cancel.connection'
    _description = "Cancel Connection Process"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'new_connection_id'
    _order = 'id DESC'

    @api.depends('connection_history_id', 'cylinder_qty', 'damage_cylinder_qty')
    def _compute_return_security_deposit(self):
        """ Calculate security deposit amount based on selected cancel
        and damage qty"""
        for rec in self:
            if rec.connection_history_id:
                security_deposit_amount = (
                  rec.connection_history_id.security_deposit_amount /
                  rec.connection_history_id.qty) * rec.cylinder_qty
                damage_deposit_amount = (
                    rec.connection_history_id.security_deposit_amount /
                    rec.connection_history_id.qty) * rec.damage_cylinder_qty
                rec.security_deposit_amount = \
                    security_deposit_amount - damage_deposit_amount
            else:
                rec.security_deposit_amount = 0.0

    new_connection_id = fields.Many2one(comodel_name='new.registration.process',
                                        string="Registration Number")
    date = fields.Datetime(string='Date and Time', required=True,
                           default=fields.Datetime.now,
                           help="New Connection Date and Time")
    partner_id = fields.Many2one(comodel_name='res.partner',
                                 related='new_connection_id.partner_id',
                                 string="Customer Name",
                                 help="Customer")
    cid_number = fields.Char(related='new_connection_id.partner_id.cid_number',
                             string='CID Number')
    cylinder_qty = fields.Integer(string="Cancel Cylinder Qty", defult=0.0)
    is_damage = fields.Boolean(string="Is Damage Empty Cylinder ?")
    is_received_damage = fields.Boolean(string="Is Received Damage Empty "
                                        "Cylinder Qty ?")
    empty_cylinder_qty = fields.Integer(string="Received Empty Cylinder Qty",
                                        defult=0.0)
    damage_cylinder_qty = fields.Integer(
        string="Damage Empty Cylinder Qty", defult=0.0)
    received_damage_cylinder_qty = fields.Integer(
        string="Received Damage Empty Cylinder Qty", defult=0.0)
    current_cylinder_qty = fields.Integer(
        related='new_connection_id.cylinder_qty',
        string="Total Number of Cylinder Qty")
    license_number = fields.Char(
        related='new_connection_id.partner_id.license_number',
        string="License Number")
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company',
        default=lambda self: self.env.user.company_id,
        help="Company of logged in user")
    currency_id = fields.Many2one(
        comodel_name='res.currency', string='Currency',
        default=lambda self: self.env.user.company_id.currency_id)
    security_deposit_amount = fields.Monetary(
        compute='_compute_return_security_deposit',
        currency_field='currency_id',
        string="Return Security Deposit Amount",
        help="Total Security Deposit Amounts", defult=0.0,)
    current_security_deposit_amount = fields.Float(
        related='new_connection_id.security_deposit_amount',
        string="Total Security Deposit Amounts",
        help="Current Total Security Deposit Amounts")
    user_id = fields.Many2one('res.users', string="Responsible",
                              default=lambda self: self.env.user,
                              help="Current User")
    state_id = fields.Many2one(related='partner_id.state_id', string="State",
                               help="State of Partner")
    phone_number = fields.Char(related='partner_id.mobile',
                               string="Customer Contact No",
                               help="Customer Contact Number")
    state = fields.Selection([('draft', 'New'),
                              ('cancel_sales_point',
                               'Surrendered by Sales Point'),
                              ('cancel_big',
                               'Surrendered by BIG'),
                              ('reject', 'Reject'),
                              ('cancel', 'Cancel')],
                             default='draft', string="Status",
                             track_visibility='onchange',
                             help="State of Cancel Connection")
    notes = fields.Text(string="Note", help="Description of the Cancel"
                                            "Connections")
    connection_history_id = fields.Many2one(comodel_name='connection.history',
                                            string="Money Receipt No")
    payment_mode = fields.Selection([('cash', 'Cash'), ('cheque', 'Cheque')],
                                    string="Payment Type", default='cash')
    cheque_no = fields.Char(string="Cheque Number")
    cheque_date = fields.Date(string="Cheque Date")

    def remaining_cancel_qty(self):
        """ Method to return remaining cancel qty"""
        remaining_qty = 0.0
        connection_history_obj = self.env['connection.history']
        for rec in self:
            cancel_qty = 0.0
            new_history_connection_id = connection_history_obj.search([
                ('money_receipt_no', '=',
                 rec.connection_history_id.money_receipt_no),
                ('type', 'in', ['Additional Connection', 'New Connection']),
            ], limit=1)
            cancel_connection_ids = connection_history_obj.search([
                ('money_receipt_no', '=',
                 rec.connection_history_id.money_receipt_no),
                ('type', '=', 'Cancel Connection')])
            for cancel_history_id in cancel_connection_ids:
                cancel_qty += cancel_history_id.qty
            remaining_qty = (new_history_connection_id.qty - cancel_qty)
        return remaining_qty

    @api.constrains('new_connection_id')
    def _check_delivered_qty(self):
        """ Method to restrict for Cancelation order before delivered"""
        for rec in self:
            if rec.new_connection_id:
                if rec.new_connection_id.remaining_qty_deliver > 0:
                    raise ValidationError(_("You can not Cancel Connection !!"
                                            "\nFirst, You have to receive %s "
                                            "remaining Register Cylinder "
                                            "Qty !!"
                                            % (rec.new_connection_id.
                                            remaining_qty_deliver)))

    @api.constrains('cylinder_qty', 'security_deposit_amount',
                    'new_connection_id', 'connection_history_id')
    def _check_cylinder_deposit(self):
        """Method to raise Validation for cylinder qty and deposit amount"""
        for rec in self:
            deposit_amount = 0.0
            if rec.state == 'draft':
                cancel_connection_ids = self.search([
                    ('id', '!=', rec.id),
                    ('new_connection_id', '=', rec.new_connection_id.id),
                    ('state', '=', 'draft')])
                if cancel_connection_ids:
                    raise ValidationError(_(
                        " %s  Cancel record already exists for Customer %s !!")
                        % (cancel_connection_ids[0].new_connection_id.number,
                            rec.partner_id.name))
            if rec.connection_history_id:
                if rec.cylinder_qty <= 0:
                    raise ValidationError(_("Cylinder Qty should not "
                                            "be less than or equal to Zero ! "))
                elif rec.security_deposit_amount < 0:
                    raise ValidationError(_("Security Deposit Amount should not"
                                            " be negative value ! "))
                if rec.cylinder_qty > self.remaining_cancel_qty():
                    raise ValidationError(_("Cylinder Qty should not "
                                            "be greater than %s Qty !!")
                                          % (self.remaining_cancel_qty()))
                deposit_amount = \
                    (rec.connection_history_id.security_deposit_amount /
                     rec.connection_history_id.qty) * rec.cylinder_qty
                if rec.security_deposit_amount > deposit_amount:
                        raise ValidationError(
                        _("Security Deposit Amount "
                          "should not be greater than %s Amount !!")
                        % deposit_amount)

    @api.constrains('is_damage', 'cylinder_qty', 'empty_cylinder_qty',
                    'damage_cylinder_qty', 'is_received_damage',
                    'received_damage_cylinder_qty')
    def _check_damage_qty(self):
        """Method to raise Validation for Received empty cylinder qty"""
        for rec in self:
            if rec.is_damage:
                if rec.empty_cylinder_qty < 0:
                    raise ValidationError(_("Received Empty Cylinder Qty "
                                            "should not be less than Zero ! "))
                elif rec.damage_cylinder_qty <= 0:
                    raise ValidationError(_("Damage Empty Cylinder "
                                            "Qty should not be less than "
                                            "or equal to Zero ! "))
                total_received_qty = rec.empty_cylinder_qty + \
                                     rec.damage_cylinder_qty
                if total_received_qty != rec.cylinder_qty :
                    raise ValidationError(_("Sum of Received Empty Cylinder "
                                            "Qty and Damage Empty "
                                            "Cylinder Qty \nshould  be "
                                            "equal to Cancel "
                                            "Cylinder Qty !! "))
                if rec.is_received_damage and rec.damage_cylinder_qty > 0 and \
                        rec.received_damage_cylinder_qty > \
                        rec.damage_cylinder_qty:
                        raise ValidationError(
                            _("Received Damage Empty Cylinder Qty "
                              "should not be greater than %s Qty !!")
                            % rec.damage_cylinder_qty)
                elif rec.is_received_damage and \
                        rec.received_damage_cylinder_qty <= 0:
                    raise ValidationError(_("Received Damage Empty Cylinder Qty"
                                            " should not be less than "
                                            "or equal to Zero ! "))

    @api.onchange('new_connection_id')
    def onchange_new_connection(self):
        """ Onchange of New Connection number set all value of
        Existing Customer Connections"""
        for rec in self:
            rec.is_damage = False
            rec.connection_history_id = False
            rec.cheque_no = False
            rec.cheque_date = False

    @api.onchange('payment_mode')
    def onchange_payment_mode(self):
        """ Onchange of Payment mode set cheque number and Date as False"""
        for rec in self:
            rec.cheque_no = False
            rec.cheque_date = False

    @api.onchange('connection_history_id')
    def onchange_receipt_no(self):
        """ Onchange of receipt number set cylinder qty and
        security deposit amount"""
        for rec in self:
            if rec.connection_history_id:
                rec.cylinder_qty = self.remaining_cancel_qty()
            else:
                rec.is_damage = False
                rec.cylinder_qty = 0.0

    @api.onchange('cylinder_qty')
    def onchange_qty(self):
        """ Onchange of cylinder quantity to set damage as false """
        for rec in self:
            if rec.cylinder_qty and rec.connection_history_id:
                rec.is_damage = False
                rec.damage_cylinder_qty = 0.0
                rec.empty_cylinder_qty = 0.0
                rec.is_received_damage = 0.0
                rec.received_damage_cylinder_qty = 0.0

    @api.onchange('is_damage', 'damage_cylinder_qty', 'is_received_damage')
    def onchange_is_damage(self):
        """ Onchange of Damage cylinder quantity to set damage
        and empty cylinder """
        for rec in self:
            if not rec.is_received_damage:
                rec.received_damage_cylinder_qty = 0.0
            if not rec.is_damage:
                rec.damage_cylinder_qty = 0.0
                rec.empty_cylinder_qty = 0.0
                rec.is_received_damage = 0.0
                rec.received_damage_cylinder_qty = 0.0
            else:
                if rec.damage_cylinder_qty > rec.cylinder_qty:
                    raise ValidationError(_("Received Damage Empty Cylinder "
                                            "Qty should not be greater than "
                                            "Cancel Cylinder qty ! "))
    def action_cancel_salepoint(self):
        """ Method used to Cancel connections by Sales Point"""
        for rec in self:
            # send Email to big manager for cancel process
            user_email_list = []
            user_obj = self.env['res.users']
            from_mail = user_obj.browse(self._uid) and user_obj.login or ''
            big_manager_grp = self.env.ref("big_general.group_big_manager")
            for user in big_manager_grp.users:
                user_email_list.append(user.partner_id.email
                                       if user.partner_id.email else '')
            email_template = self.env.ref(
                'big_new_registration.email_surrender_connection_request')
            if email_template and user_email_list:
                user_email = ','.join(user_email_list)
                email_template.sudo().write({
                    'email_from': from_mail,
                    'email_to': user_email
                })
                email_template.send_mail(self.id, force_send=True)
            rec.state = 'cancel_sales_point'
            if rec.new_connection_id.cylinder_qty == 0:
                rec.new_connection_id.state = 'cancel_sales_point'

    def create_picking_order(self, destination_location_id, cylinder_qty):
        """ Method used to create Incoming shipment for Empty cylinder
         and damage cylinder by respective location."""
        for rec in self:
            in_pick_vals = {}
            incoming_move_list = []
            if not rec.user_id.warehouse_id and rec.user_id.stock_location_id:
                raise ValidationError(_
                                      ("Please Configure Warehouse "
                                       "and Stock locations !! "))
            incoming_picking_id = self.env['stock.picking.type'].search(
                [('code', '=', 'incoming'),
                 ('warehouse_id', '=', rec.user_id.warehouse_id.id),
                 ('company_id', '=', rec.company_id.id )], limit=1)
            location_id = self.env['stock.location'].search([
                ('usage', '=', 'customer'),
                ], limit=1)
            product_id = self.env['product.product'].search(
                [('is_empty_cylinder_product', '=', True)], limit=1)
            # create move line for incoming shipment
            move_line_vals_incoming = (0, 0, {
                'name': '/',
                'date': fields.Datetime.now(),
                'location_dest_id': destination_location_id or False,
                'location_id': location_id and location_id.id or False,
                'product_id': product_id and product_id.id or False,
                'product_uom': product_id.uom_id
                and product_id.uom_id.id or False,
                'quantity_done': cylinder_qty or 0.0,
                'product_uom_qty' : cylinder_qty or 0.0,
                'company_id': rec.company_id.id,
            })
            incoming_move_list.append(move_line_vals_incoming)
            in_pick_vals.update({
                'location_dest_id': destination_location_id or False,
                'location_id': location_id and location_id.id or False,
                'picking_type_id': incoming_picking_id.id or False,
                'move_ids_without_package': incoming_move_list,
            })
            if in_pick_vals:
                incoming_shipment_id = self.env['stock.picking'].create(
                    in_pick_vals)
                incoming_shipment_id.button_validate()

    def create_journal_entry(self, new_connection_id, security_deposit_amount):
        """ Create journal entry for receive damage security deposit"""
        account_obj = self.env['account.account']
        name = "Security Deposit Receive for " \
               "Damage Qty of %s" % (new_connection_id.number)
        debit_account_id = account_obj.search([
            ('user_type_id', '=',
             self.env.ref('account.data_account_type_current_liabilities').id),
            ('company_id', '=', self.env.user.company_id.id),
            ('code', '=', '3109000')], limit=1)
        credit_account_id = account_obj.search([
            ('user_type_id', '=',
             self.env.ref('account.data_account_type_revenue').id),
            ('company_id', '=', self.env.user.company_id.id),
            ('code', '=', '4100000')], limit=1)
        debit_vals = {
            'name': name,
            'partner_id': new_connection_id.partner_id.id or False,
            'account_id': debit_account_id and debit_account_id.id or False,
            'debit': security_deposit_amount,
            'credit': 0.0,
        }
        credit_vals = {
            'name': name,
            'partner_id': new_connection_id.partner_id.id or False,
            'account_id': credit_account_id and credit_account_id.id or False,
            'debit': 0.0,
            'credit': security_deposit_amount,
        }
        #MOVE CREATE
        vals = {
            'ref': name,
            'journal_id': self.env['account.journal'].search([
                        ('company_id', '=', self.env.company.id),
                        ('type', '=', 'cash')], limit=1).id,
            'state': 'draft',
            'company_id': self.company_id.id,
            'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
        }
        move_id = self.env['account.move'].create(vals)
        return move_id

    def action_cancel_big(self):
        """ Method used to Cancel connections by BIG"""
        for rec in self:
            cancel_qty = 0.0
            if rec.current_cylinder_qty <= 0:
                raise ValidationError(_("You can not approve this record !! \n"
                                        "Total number of Cylinder Qty "
                                        "is  %s !!")
                                      % rec.current_cylinder_qty)
            user_email_list = []
            # Create connection history for cancel connection
            history_id = self.env['connection.history'].create({
                'new_connection_id': rec.new_connection_id
                and rec.new_connection_id.id or False,
                'type': 'Cancel Connection',
                'date': rec.date,
                'qty': rec.cylinder_qty or 0.0,
                'security_deposit_amount': rec.security_deposit_amount or 0.0,
                'money_receipt_no': rec.connection_history_id.money_receipt_no,
                'payment_mode': rec.payment_mode,
                'cheque_no': rec.cheque_no or False,
                'cheque_date': rec.cheque_date or False,
                'state': 'done',
            })
            new_history_connection_id = self.env['connection.history'].search([
                ('money_receipt_no', '=',
                 rec.connection_history_id.money_receipt_no),
                ('type', 'in', ['Additional Connection', 'New Connection']),
            ], limit=1)
            cancel_connection_ids = self.env['connection.history'].search([
                ('money_receipt_no', '=',
                 rec.connection_history_id.money_receipt_no),
                ('type', '=', 'Cancel Connection')])
            for cancel_history_id in cancel_connection_ids:
                cancel_qty += cancel_history_id.qty
            remaining_qty = new_history_connection_id.qty - cancel_qty
            if remaining_qty == 0:
                new_history_connection_id.is_cancel_qty = True
            if rec.is_damage and rec.damage_cylinder_qty:
                security_deposit_amount = \
                    (rec.connection_history_id.security_deposit_amount /
                     rec.connection_history_id.qty) * rec.damage_cylinder_qty
                # Create Journal Entry for Receive damage Cylinder Qty
                # Security deposit
                move_id = rec.create_journal_entry(rec.new_connection_id,
                                                   security_deposit_amount)
                move_id.action_post()
                rec.new_connection_id.security_deposit_amount -= \
                    security_deposit_amount
            # Create Payment for vendor to return security deposit
            self.env['account.payment'].with_context({
                'security_deposit': True}).create({
                    'partner_type': 'supplier',
                    'payment_type': 'outbound',
                    'amount': rec.security_deposit_amount or 0.0,
                    'journal_id': self.env['account.journal'].search([
                        ('company_id', '=', self.env.company.id),
                        ('type', 'in', ('bank', 'cash'))], limit=1).id,
                    'payment_method_id': self.env.ref(
                        "account.account_payment_method_manual_out").id,
                    'partner_id': rec.new_connection_id.partner_id.id,
                    'communication':
                        'Return Security Deposit for Connection ' +
                        str(rec.new_connection_id.number),
                    'company_id': rec.company_id.id,
                    'currency_id': rec.currency_id.id,
                    'new_connection_id': rec.new_connection_id.id,
                    'history_connection_id': history_id and history_id.id,
            })
            # Send cancel approved Email notification for Sale users
            user = self.env['res.users']
            from_mail = user.browse(self._uid) and user.login or ''
            if rec.user_id and rec.user_id.login:
                user_email_list.append(rec.user_id.login)
            account_grp = self.env.ref("account.group_account_manager")
            # List of users which have account group assign
            for user in account_grp.users:
                if user.partner_id.email not in user_email_list:
                    user_email_list.append(user.partner_id.email
                                           if user.partner_id.email else '')
            email_template = \
                self.env.ref('big_new_registration.'
                             'email_surrender_connection_approve_big')
            if email_template and user_email_list:
                user_email = ','.join(user_email_list)
                email_template.sudo().write({
                    'email_from': from_mail,
                    'email_to': user_email
                })
                email_template.send_mail(self.id, force_send=True)
            rec.new_connection_id.cylinder_qty -= rec.cylinder_qty
            rec.new_connection_id.security_deposit_amount -= \
                rec.security_deposit_amount
            rec.state = 'cancel_big'
            # Create empty cylinder picking and customer Damage picking
            # Customer stock Location
            stock_location_id = rec.user_id.stock_location_id and \
                                rec.user_id.stock_location_id.id or False
            damage_location_id = rec.user_id.customer_damage_location_id and \
                                 rec.user_id.customer_damage_location_id.id or \
                                 False
            if rec.is_damage:
                # Create Incoming shipment for empty cylinder
                if rec.empty_cylinder_qty > 0:
                    rec.create_picking_order(stock_location_id,
                                             rec.empty_cylinder_qty)
                # Create Incoming shipment for Damage empty cylinder
                if rec.is_received_damage and \
                        rec.received_damage_cylinder_qty > 0:
                    rec.create_picking_order(damage_location_id,
                                             rec.received_damage_cylinder_qty)
            else:
                rec.create_picking_order(stock_location_id, rec.cylinder_qty)
            if rec.new_connection_id.cylinder_qty == 0:
                rec.new_connection_id.state = 'cancel_big'
                rec.new_connection_id.partner_id.is_pos_customer = False
                rec.new_connection_id.partner_id.barcode = ''

    def action_reject(self):
        """ Method used to Reject Cancel connections"""
        for rec in self:
            if rec.new_connection_id.cylinder_qty <= 0:
                raise ValidationError(_("%s order is "
                                        "already surrendered !! \n"
                                        "Please do cancel order !!")
                                      % rec.new_connection_id.number)
            # Send Surrender request Reject Email notification for Sale users
            user = self.env['res.users']
            from_mail = user.browse(self._uid) and user.login or ''
            if rec.user_id and rec.user_id.login:
                to_mail = rec.user_id.login or ''
                email_template = self.env.ref(
                    'big_new_registration.'
                    'email_surrender_connection_reject_big')
                if email_template:
                    email_template.sudo().write({
                        'email_from': from_mail,
                        'email_to': to_mail
                    })
                    email_template.send_mail(self.id, force_send=True)
            rec.state = 'reject'

    def action_cancel(self):
        """ Method used to Cancel surrender connections"""
        for rec in self:
            rec.state = 'cancel'
