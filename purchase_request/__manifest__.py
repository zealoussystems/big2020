# See LICENSE file for full copyright and licensing details.

{
    "name": "Purchase Request",
    "category": "Purchase Management",
    'version': '13.0.1.0.0',
    'license': 'LGPL-3',
    "summary": "Use this module to have notification of requirements of "
               "materials and/or external services and keep track of such "
               "requirements.",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "depends": [
        "purchase",
        "product",
        "purchase_stock",
    ],
    "data": [
        "security/purchase_request.xml",
        "security/ir.model.access.csv",
        "data/purchase_request_sequence.xml",
        "data/purchase_request_data.xml",
        "reports/report_purchase_request.xml",
        "views/purchase_request_view.xml",
        "views/purchase_request_line_view_1.xml",
        "views/purchase_request_report.xml",
        "views/product_template.xml",
        "views/purchase_order_view.xml",
        "views/stock_move_views.xml",
        "wizard/purchase_request_line_make_purchase_order_view.xml",
    ],
    'demo': [
        "demo/purchase_request_demo.xml",
    ],
    'installable': True,
    'application': True,
}
