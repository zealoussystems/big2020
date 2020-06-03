# © 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'BIG - General',
    'version': '13.0.1.0.0',
    'category': '',
    'summary': 'BIG General',
    'author': "Serpent Consulting Services Pvt. Ltd.",
    'website': "http://www.serpentcs.com",
    'license': 'AGPL-3',
    'depends': ['base','product','account'],
    'data': [
        'security/big_general_security_view.xml',
        'views/menu_item_view.xml',
        'views/res_company_extended_view.xml',
        'views/product_extended_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
