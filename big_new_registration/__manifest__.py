# © 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'BIG - New Registration Process',
    'version': '13.0.1.0.0',
    'category': 'BIG',
    'summary': 'BIG New Connection Process',
    'author': "Serpent Consulting Services Pvt. Ltd.",
    'website': "http://www.serpentcs.com",
    'license': 'AGPL-3',
    'depends': ['base', 'mail', 'portal', 'big_general', 'account',
                'big_res_partner_barcode'],
    'data': [
        'security/new_registration_security.xml',
        'security/ir.model.access.csv',
        'data/new_connection_sequence.xml',
        'data/email_template_view.xml',
        'views/big_new_registration_process_view.xml',
        'views/res_partner_extended_view.xml',
        'views/big_cancel_registration_process_view.xml',
        'views/big_security_configuration_view.xml',
        'wizard/registration_wizard_view.xml',
        'wizard/big_cancel_reg_wizard_view.xml',
        'report/registration_report.xml',
        'report/registration_template_view.xml',
        'report/cancel_connection_template_view.xml',
        'report/payment_receipt_template_view.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}