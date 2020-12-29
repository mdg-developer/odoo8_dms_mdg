# -*- coding: utf-8 -*-
#################################################################################
#
#Copyright (c) 2015-Present TidyWay Software Solution. (<https://tidyway.in/>)
#
#################################################################################


{
    'name': 'Stock Inventory Report',
    'version': '1.0',
    'category':'stock',
    'summary': 'Real Time Inventory Chart.',
    'description': """


Day to Day Stock Counting,
----------------------------
 * Starting Inventory
 * Sold Goods
 * Received Goods
 * Internal Movements Goods
 * Adjustment Goods
 * Ending Inventory

Multiple Dates Inventory,
----------------------------
 * Starting Inventory
 * Sold Goods
 * Received Goods
 * Internal Movements Goods
 * Adjustment Goods
 * Ending Inventory

Group By,
----------------------------
 * Warehouse
 * Product Category
""",
    'author': 'TidyWay',
    'website': 'http://www.tidyway.in',
    'depends': ['stock','report'],
    'data': [
        'security/inventory_report_security.xml',
        'wizard/inventory_wizard.xml',
        'inventory_report.xml',
        'views/inventory_report_by_warehouse.xml',
        'views/inventory_report_by_category.xml'
    ],
    'price': 65,
    'currency': 'EUR',
    'installable': True,
    'application': True,
    'auto_install': False,
    'images' : ['images/inv.jpeg'],
    'live_test_url':  'https://www.youtube.com/watch?v=LfaN3kbF32s'
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
