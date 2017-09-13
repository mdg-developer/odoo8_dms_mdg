# -*- coding: utf-8 -*-



{
    'name': 'Purchase landed costs - Alternative option',
    'version': '8.0.2.5.0',
    'author': 'Seventh Computing',
    'category': 'Purchase Management',
    'website': 'http://www.7thcomputing.com',
    'summary': 'Purchase cost distribution',
    'depends': [
        'stock',
        'purchase',
    ],
    'data': [
        'wizard/picking_import_wizard_view.xml',
        'wizard/import_invoice_line_wizard_view.xml',
        'wizard/import_landed_cost_pickings_wizard_view.xml',
        'views/account_invoice_view.xml',
        'views/purchase_cost_distribution_view.xml',
        'views/purchase_cost_distribution_line_expense_view.xml',
        'views/purchase_expense_type_view.xml',
        'views/purchase_order_view.xml',
        'views/stock_picking_view.xml',
        'data/purchase_cost_distribution_sequence.xml',
        'security/purchase_landed_cost_security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
#     'images': [
#         '/static/description/images/purchase_order_expense_main.png',
#         '/static/description/images/purchase_order_expense_line.png',
#         '/static/description/images/expenses_types.png',
#     ],
}
