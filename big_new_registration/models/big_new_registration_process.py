# See LICENSE file for full copyright and licensing details.
from datetime import date, datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class NewRegistrationProcess(models.Model):
    """ This Class Create for New Connection Registration Process"""

    _name = 'new.registration.process'
    _description = "New Connection Process"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'number'
    _order = 'id DESC'

    @api.depends('cylinder_qty', 'date')
    def _compute_security_amount(self):
        """ Calculate security deposit based on config amount and qty"""
        for rec in self:
            if rec.cylinder_qty and rec.state == 'draft':
                security_amount_ids = self.env['security.config'].search(
                    [('start_date', '<=', rec.date),
                     ('end_date', '>=', rec.date)])
                if security_amount_ids:
                    rec.security_deposit_amount = \
                        security_amount_ids[0].security_deposit_amount * \
                        rec.cylinder_qty
                else:
                    raise ValidationError(_("Please Configure Security Deposit"
                                            " Amounts !"))

    number = fields.Char(string='Number', default='New',
                         help="Sequence Number", copy=False)
    date = fields.Datetime(string='Date and Time', required=True,
                             default=fields.Datetime.now,
                             help="New Connection Date and Time")
    partner_id = fields.Many2one(comodel_name='res.partner',
                                 string="Customer Name",
                                 help="Customer")
    cid_number = fields.Char(related='partner_id.cid_number',
                             string='CID Number', help="Identification Number")
    money_receipt_no = fields.Char(string='Money Receipt No')
    cylinder_qty = fields.Integer(string="Cylinder Qty")
    license_number = fields.Char(related='partner_id.license_number',
                                 string="License Number")
    security_deposit_amount = fields.Float(
        compute='_compute_security_amount', store=True,
        string="Security Deposit Amount",
        help="Total Security Deposit Amounts")
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company',
        default=lambda self: self.env.user.company_id,
        help="Company of logged in user")
    currency_id = fields.Many2one(
        comodel_name='res.currency', string='Currency',
        default=lambda self: self.env.user.company_id.currency_id)
    user_id = fields.Many2one('res.users', string="Responsible",
                              default=lambda self: self.env.user,
                              help="Current User")
    state_id = fields.Many2one(related='partner_id.state_id', string="State",
                               help="State of Partner")
    phone_number = fields.Char(related='partner_id.mobile',
                               string="Customer Contact No",
                               help="Customer Contact Number")
    state = fields.Selection([('draft', 'New'),
                              ('confirm', 'Approved by Sales Point'),
                              ('done', 'Approved by BIG'),
                              ('reject', 'Reject'),
                              ('cancel_sales_point',
                               'Surrendered by Sales Point'),
                              ('cancel_big',
                               'Surrendered by BIG'),
                              ('cancel', 'Cancel')],
                             default='draft', string="Status",
                             track_visibility='onchange',
                             help="State of new Connection")
    additional_connection_ids = fields.One2many(
        'additional.connection', 'new_connection_id',
        string="Additional Connections")
    connection_history_ids = fields.One2many(
        'connection.history', 'new_connection_id',
        string="Connections History")
    account_payment_ids = fields.One2many(
        'account.payment', 'new_connection_id',
        string="Payment History")
    payment_mode = fields.Selection([('cash', 'Cash'), ('cheque', 'Cheque')],
                                    string="Payment Type", default='cash')
    cheque_no = fields.Char(string="Cheque Number")
    cheque_date = fields.Date(string="Cheque Date")
    notes = fields.Text(string="Note", help="Description of the New"
                                            "Connections")

    @api.constrains('partner_id', 'cylinder_qty')
    def _check_cylinder_qty(self):
        """Method to raise Validation for CID number less then 11 digits"""
        for rec in self:
            if rec.state == 'draft':
                if rec.state not in ['cancel_big', 'cancel', 'reject']:
                    new_connection_ids = self.search([
                        ('id', '!=', rec.id),
                        ('partner_id', '=', rec.partner_id.id),
                        ('state', 'not in',
                         ['cancel_big', 'cancel', 'reject'])])
                    if new_connection_ids:
                        raise ValidationError(_(
                            " %s  have already exists Connection !! \n"
                            " Please update connection on "
                            "Registration Number :  %s ")
                        %(rec.partner_id.name, new_connection_ids[0].number))
                if rec.cylinder_qty <= 0:
                    raise ValidationError(_("Cylinder Qty should not "
                                            "be less than or equal "
                                            "to Zero ! "))

    @api.onchange('payment_mode')
    def onchange_payment_mode(self):
        """ Onchange of Payment mode set cheque number and Date as False"""
        for rec in self:
            rec.cheque_no = False
            rec.cheque_date = False

    # def action_confirm(self):
    #     """ Method used to Confirm new connections"""
    #     for rec in self:
    #         if not rec.state_id:
    #             raise ValidationError(_("Please select Location "
    #                                     "from Customer Form (state) !!"))
    #         user = self.env['res.users']
    #         from_mail = user.browse(self._uid) and user.login or ''
    #         from_mail = from_mail.encode('utf-8')
    #         groups = []
    #         groups.extend(user.search([]).filtered(
    #             lambda x: x.has_group("big_general.group_big_manager")).ids)
    #         users = list(set(groups))
    #         to_mail_list = []
    #         for user_id in users:
    #             big_manager = user.browse(user_id)
    #             if big_manager.login:
    #                 to_mail_list.append(str(big_manager.login.encode('utf-8')))
    #         if to_mail_list:
    #             to_mail = ','.join(to_mail_list)
    #             email_template = self.env.ref(
    #                 'big_new_registration.email_new_connection_request')
    #             if email_template:
    #                 email_template.sudo().write({
    #                     'email_from': from_mail,
    #                     'email_to': to_mail
    #                 })
    #                 email_template.send_mail(self.id, force_send=True)
    #         f_year = datetime.strftime(datetime.now(), "%y")
    #         sequence = self.env['ir.sequence'].next_by_code(
    #             'money.receipt.sequence')
    #         seq_str = str(rec.partner_id.state_id.code) + '-' + f_year + '-' \
    #                   + sequence
    #         rec.money_receipt_no = str(seq_str)
    #         # Create Connection History
    #         self.env['connection.history'].create({
    #             'new_connection_id': rec.id,
    #             'type': 'New Connection',
    #             'date': rec.date,
    #             'qty': rec.cylinder_qty or 0.0,
    #             'security_deposit_amount': rec.security_deposit_amount or 0.0,
    #             'money_receipt_no': rec.money_receipt_no,
    #             'payment_mode': rec.payment_mode,
    #             'cheque_no': rec.cheque_no or False,
    #             'cheque_date': rec.cheque_date or False,
    #         })
    #         rec.state = 'confirm'

    def action_confirm(self):
        """ Method used to Confirm new connections"""
        for rec in self:
            if not rec.state_id:
                raise ValidationError(_("Please select Location "
                                        "from Customer Form (state) !!"))
            user_email_list = []
            user_obj = self.env['res.users']
            from_mail = user_obj.browse(self._uid) and user_obj.login or ''
            big_manager_grp = self.env.ref("big_general.group_big_manager")
            for user in big_manager_grp.users:
                user_email_list.append(user.partner_id.email
                                       if user.partner_id.email else '')
            email_template = self.env.ref(
                'big_new_registration.email_new_connection_request')
            if email_template and user_email_list:
                user_email = ','.join(user_email_list)
                email_template.sudo().write({
                    'email_from': from_mail,
                    'email_to': user_email
                })
                email_template.send_mail(self.id, force_send=True)
            f_year = datetime.strftime(datetime.now(), "%y")
            sequence = self.env['ir.sequence'].next_by_code(
                'money.receipt.sequence')
            seq_str = str(rec.partner_id.state_id.code) + '-' + f_year + '-' \
                      + sequence
            rec.money_receipt_no = str(seq_str)
            # Create Connection History
            self.env['connection.history'].create({
                'new_connection_id': rec.id,
                'type': 'New Connection',
                'date': rec.date,
                'qty': rec.cylinder_qty or 0.0,
                'security_deposit_amount': rec.security_deposit_amount or 0.0,
                'money_receipt_no': rec.money_receipt_no,
                'payment_mode': rec.payment_mode,
                'cheque_no': rec.cheque_no or False,
                'cheque_date': rec.cheque_date or False,
            })
            rec.state = 'confirm'

    def action_done(self):
        """ Method used to Done new connections by BIG Manager"""
        for rec in self:
            user_email_list = []
            user_obj = self.env['res.users']
            f_year = datetime.strftime(datetime.now(), "%Y")
            sequence = self.env['ir.sequence'].next_by_code(
                'new.registration.process')
            seq_str = sequence[:4] + f_year + sequence[3:]
            rec.number = str(seq_str)
            history_id = self.env['connection.history'].search([
                ('new_connection_id', '=', rec.id)], limit=1)
            if history_id:
                history_id.state = 'done'
            # Create Payment for security deposit and post
            self.env['account.payment'].create({
                'partner_type': 'customer',
                'payment_type': 'inbound',
                'amount': rec.security_deposit_amount,
                'journal_id': self.env['account.journal'].search([
                    ('company_id', '=', self.env.company.id),
                    ('type', '=', 'cash')], limit=1).id,
                'payment_method_id': self.env.ref(
                    "account.account_payment_method_manual_in").id,
                'partner_id': rec.partner_id.id,
                'communication':
                    'Security Deposit for New Connection ' + str(rec.number),
                'company_id': rec.company_id.id,
                'currency_id': rec.currency_id.id,
                'new_connection_id': rec.id,
            }).post()
            # Send Approved Email notification for Sale users and accountant
            from_mail = user_obj.browse(self._uid) and user_obj.login or ''
            if rec.user_id and rec.user_id.login:
                user_email_list.append(rec.user_id.login)
            account_grp = self.env.ref("account.group_account_manager")
            # List of users which have account group assign
            for user in account_grp.users:
                if user.partner_id.email not in user_email_list:
                    user_email_list.append(user.partner_id.email
                                           if user.partner_id.email else '')
            email_template = self.env.ref(
                'big_new_registration.email_new_connection_approve_big')
            if email_template and user_email_list:
                user_email = ','.join(user_email_list)
                email_template.sudo().write({
                    'email_from': from_mail,
                    'email_to': user_email
                })
                email_template.send_mail(self.id, force_send=True)
            rec.state = 'done'
            rec.partner_id.is_pos_customer = True
            rec.partner_id.barcode = str(seq_str)

    def action_reject(self):
        """ Method used to Reject new connections"""
        for rec in self:
            # Send Reject Email notification for Sale users
            user = self.env['res.users']
            from_mail = user.browse(self._uid) and user.login or ''
            from_mail = from_mail.encode('utf-8')
            if rec.user_id and rec.user_id.login:
                to_mail = rec.user_id.login.encode('utf-8')
                email_template = self.env.ref(
                    'big_new_registration.email_new_connection_reject_big')
                if email_template:
                    email_template.sudo().write({
                        'email_from': from_mail,
                        'email_to': to_mail
                    })
                    email_template.send_mail(self.id, force_send=True)
            history_id = self.env['connection.history'].search([
                ('new_connection_id', '=', rec.id)], limit=1)
            if history_id:
                history_id.state = 'reject'
            rec.state = 'reject'

    def action_cancel(self):
        """ Method used to Cancel new connections"""
        for rec in self:
            rec.partner_id.register_qty = 0
            history_id = self.env['connection.history'].search([
                ('new_connection_id', '=', rec.id)], limit=1)
            if history_id:
                history_id.state = 'cancel'
            rec.state = 'cancel'

    def action_reset_to_draft(self):
        """ Method used to Reset new connections"""
        for rec in self:
            new_connection_ids = self.search([
                ('id', '!=', rec.id),
                ('partner_id', '=', rec.partner_id.id),
                ('state', 'not in', ['cancel_big', 'reject'])])
            if new_connection_ids:
                raise ValidationError(_("Record already Exists !!"))
            rec.state = 'draft'
            rec.money_receipt_no = ''

    def action_card_replacement(self):
        """ Method used to Send Email Notification for New Customer Card"""
        user_email_list = []
        user_obj = self.env['res.users']
        from_mail = user_obj.browse(self._uid) and user_obj.login or ''
        big_manager_grp = self.env.ref("big_general.group_big_manager")
        for user in big_manager_grp.users:
            user_email_list.append(user.partner_id.email
                                   if user.partner_id.email else '')
        email_template = self.env.ref(
            'big_new_registration.email_new_card_request')
        if email_template and user_email_list:
            user_email = ','.join(user_email_list)
            email_template.sudo().write({
                'email_from': from_mail,
                'email_to': user_email
            })
            email_template.send_mail(self.id, force_send=True)

class NewAdditionalConnections(models.Model):
    """ This class create for Additional connection of Existing Customer"""

    _name = 'additional.connection'
    _rec_name = 'new_connection_id'
    _description = 'Additional Connection'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    @api.depends('qty')
    def _compute_security_amount(self):
        """ Calculate security deposit based on config amount and qty"""
        for rec in self:
            if rec.qty:
                security_amount_ids = self.env['security.config'].search(
                    [('start_date', '<=', rec.date),
                     ('end_date', '>=', rec.date)])
                if security_amount_ids:
                    rec.security_deposit_amount = \
                        security_amount_ids[0].security_deposit_amount * \
                        rec.qty
                else:
                    raise ValidationError(_("Please Configure Security Deposit"
                                            " Amounts !"))

    date = fields.Datetime(string="Date and time",
                           default=fields.Datetime.now)
    qty = fields.Integer(string="Cylinder Qty")
    new_connection_id = fields.Many2one('new.registration.process',
                                        string="New Conection Reference")
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company',
        default=lambda self: self.env.user.company_id,
        help="Company of logged in user")
    currency_id = fields.Many2one(
        comodel_name='res.currency', string='Currency',
        default=lambda self: self.env.user.company_id.currency_id)
    security_deposit_amount = fields.Float(
        compute='_compute_security_amount', store=True,
        string="Security Deposit Amount",
        help="Total Security Deposit Amounts")
    money_receipt_no = fields.Char(string='Money Receipt No')
    payment_mode = fields.Selection([('cash', 'Cash'), ('cheque', 'Cheque')],
                                    string="Payment Type", default='cash')
    cheque_no = fields.Char(string="Cheque Number")
    cheque_date = fields.Date(string="Cheque Date")
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Approved by Sales Point'),
                              ('done', 'Approved by BIG'),
                              ('reject', 'Reject'),
                              ('cancel', 'Cancel')], default='draft',
                             track_visibility='onchange')

    @api.constrains('qty')
    def _check_qty_security_amount(self):
        """Method to raise Validation for CID number less then 11 digits"""
        for rec in self:
            if rec.qty <= 0:
                raise ValidationError(_("Additional Connection Cylinder Qty "
                                        "should not be less than or "
                                        "equal to Zero ! "))

    @api.onchange('payment_mode')
    def onchange_payment_mode(self):
        """ Onchange of Payment mode set cheque number and Date as False"""
        for rec in self:
            rec.cheque_no = False
            rec.cheque_date = False

    def additional_action_confirm(self):
        """ Method used to Confirm Additional connections"""
        for rec in self:
            if rec.new_connection_id:
                # Send Email to Big For Confirmation of Additional Connection
                user_email_list = []
                user_obj = self.env['res.users']
                from_mail = user_obj.browse(self._uid) and user_obj.login or ''
                big_manager_grp = self.env.ref("big_general.group_big_manager")
                for user in big_manager_grp.users:
                    user_email_list.append(user.partner_id.email
                                           if user.partner_id.email else '')
                email_template = self.env.ref(
                    'big_new_registration.email_additional_connection_request')
                if email_template and user_email_list:
                    user_email = ','.join(user_email_list)
                    email_template.sudo().write({
                        'email_from': from_mail,
                        'email_to': user_email
                    })
                    email_template.send_mail(self.id, force_send=True)
                rec.state = 'confirm'
                f_year = datetime.strftime(datetime.now(), "%y")
                sequence = self.env['ir.sequence'].next_by_code(
                    'money.receipt.sequence')
                seq_str = str(
                    rec.new_connection_id.partner_id.state_id.code) + '-' + \
                          f_year + '-' + sequence
                rec.money_receipt_no = str(seq_str)
                message = "Additional Connection Status : New -> " \
                          "Approved by Sale Point"
                rec.new_connection_id.message_post(body=message)
                # Create Connection History
                self.env['connection.history'].create({
                    'new_connection_id':
                        rec.new_connection_id and rec.new_connection_id.id
                        or False,
                    'additional_connection_id': rec.id,
                    'type': 'Additional Connection',
                    'date': rec.date,
                    'qty': rec.qty or 0.0,
                    'security_deposit_amount':
                        rec.security_deposit_amount or 0.0,
                    'money_receipt_no': rec.money_receipt_no,
                    'payment_mode': rec.payment_mode,
                    'cheque_no': rec.cheque_no or False,
                    'cheque_date': rec.cheque_date or False,
                })
        return True

    def additional_action_done(self):
        """ Method used to Done Additional connections"""
        for rec in self:
            user_email_list = []
            user = self.env['res.users']
            if rec.new_connection_id:
                history_id = self.env['connection.history'].search([
                    ('additional_connection_id', '=', rec.id)], limit=1)
                if history_id:
                    history_id.state = 'done'
                rec.new_connection_id.cylinder_qty += rec.qty
                rec.new_connection_id.security_deposit_amount += \
                    rec.security_deposit_amount
                rec.state = 'done'
                # Create Payment for security deposit and post
                self.env['account.payment'].create({
                    'partner_type': 'customer',
                    'payment_type': 'inbound',
                    'amount': rec.security_deposit_amount or 0.0,
                    'journal_id': self.env['account.journal'].search([
                        ('company_id', '=', self.env.company.id),
                        ('type', '=', 'cash')], limit=1).id,
                    'payment_method_id': self.env.ref(
                        "account.account_payment_method_manual_in").id,
                    'partner_id': rec.new_connection_id.partner_id.id,
                    'communication':
                        'Security Deposit for Additional Connection ' +
                        str(rec.new_connection_id.number),
                    'company_id': rec.company_id.id,
                    'currency_id': rec.currency_id.id,
                    'new_connection_id': rec.new_connection_id.id,
                }).post()
                # Send Approved Email notification for Sale users
                from_mail = user.browse(self._uid) and user.login or ''
                if rec.new_connection_id.user_id and \
                        rec.new_connection_id.user_id.login:
                    user_email_list.append(rec.new_connection_id.user_id.login)
                account_grp = self.env.ref("account.group_account_manager")
                # List of users which have account group assign
                for user in account_grp.users:
                    if user.partner_id.email not in user_email_list:
                        user_email_list.append(user.partner_id.email
                                               if user.partner_id.email
                                               else '')
                email_template = self.env.ref(
                    'big_new_registration.'
                    'email_additional_connection_approve_big')
                if email_template and user_email_list:
                    user_email = ','.join(user_email_list)
                    email_template.sudo().write({
                        'email_from': from_mail,
                        'email_to': user_email
                    })
                    email_template.send_mail(self.id, force_send=True)
                message = "Additional Connection Status : " \
                  "Approved by Sales Point -> Approved by BIG"
                rec.new_connection_id.message_post(body=message)
        return True

    def additional_action_reject(self):
        """ Method used to Reject Additional connections"""
        for rec in self:
            # Send Reject Email notification for Sale users
            user = self.env['res.users']
            from_mail = user.browse(self._uid) and user.login or ''
            if rec.new_connection_id.user_id and \
                    rec.new_connection_id.user_id.login:
                to_mail = rec.new_connection_id.user_id.login
                email_template = self.env.ref(
                    'big_new_registration.'
                    'email_additional_connection_reject_big')
                if email_template:
                    email_template.sudo().write({
                        'email_from': from_mail,
                        'email_to': to_mail
                    })
                    email_template.send_mail(self.id, force_send=True)
            rec.state = 'reject'
            message = "Additional Connection Status : " \
                      "Approved by BIG -> Reject"
            rec.new_connection_id.message_post(body=message)
            history_id = self.env['connection.history'].search([
                ('additional_connection_id', '=', rec.id)], limit=1)
            if history_id:
                history_id.state = 'reject'
        return True

    def additional_action_cancel(self):
        """ Method used to Cancel Additional connections"""
        for rec in self:
            rec.state = 'cancel'
            history_id = self.env['connection.history'].search([
                ('additional_connection_id', '=', rec.id)], limit=1)
            if history_id:
                history_id.state = 'cancel'
            rec.new_connection_id.message_post(
                body="Additional Connection Status : Cancel")
        return True

    def additional_action_reset_to_draft(self):
        """ Method used to Reset Additional connections"""
        for rec in self:
            rec.state = 'draft'
            rec.new_connection_id.message_post(
                body="Additional Connection Status : Reset to Draft")
        return True
