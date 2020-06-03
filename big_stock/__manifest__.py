# © 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'BIG - Stock Management',
    'version': '13.0.1.0.0',
    'category': 'BIG',
    'summary': 'BIG Stock Process',
    'author': "Serpent Consulting Services Pvt. Ltd.",
    'website': "http://www.serpentcs.com",
    'license': 'AGPL-3',
    'depends': ['stock', 'big_general'],
    'data': [
        'security/stock_picking_security_view.xml',
        'views/big_stock_view.xml',
        'views/stock_report_extended_view.xml',
        'views/res_users_extended_view.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}