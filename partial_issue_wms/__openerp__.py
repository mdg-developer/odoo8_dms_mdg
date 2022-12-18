{
    'name': 'Partial Issue WMS',
    'version': '1.0',
    'category': 'stock',
    'sequence': 30,
    'summary': 'stock',
    'description': """
WMS Partial Issue

""",
    'author': 'Seventh Computing',
    'website': 'http://www.7thcomputing.com',
    'depends': ['branch_inventory_transfer'],
    'data': [
            'views/branch_stock_requisition.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
