# © 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'BIG - Point of Sales',
    'version': '13.0.1.0.0',
    'category': 'BIG',
    'summary': 'BIG Point of sales',
    'author': "Serpent Consulting Services Pvt. Ltd.",
    'website': "http://www.serpentcs.com",
    'license': 'AGPL-3',
    'depends': ['point_of_sale', 'big_new_registration'],
    'data': [
        'security/ir.model.access.csv',
        'security/pos_session_security_view.xml',
        'views/pos_template_extended_view.xml',
        'views/pos_extended_view.xml',
        'views/res_users_extended_view.xml',
        'wizard/pos_extended_wizard_view.xml',
        'report/pos_extended_report_view.xml',
        'report/pos_extended_report_temp.xml',
    ],
    'qweb': ['static/src/xml/pos_order_extended_view.xml'],
    'demo': [],
    'installable': True,
    'auto_install': False,
}