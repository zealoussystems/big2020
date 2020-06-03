# © 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'BIG - Account Management',
    'version': '13.0.1.0.0',
    'category': 'BIG',
    'summary': 'BIG Account Process',
    'author': "Serpent Consulting Services Pvt. Ltd.",
    'website': "http://www.serpentcs.com",
    'license': 'AGPL-3',
    'depends': ['account', 'big_general', 'account_check_printing', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_view.xml',
        'views/account_payment_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}