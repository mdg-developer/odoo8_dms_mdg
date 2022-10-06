{
    'name': 'Stock Opening',
    'version': '1.0',
    'category': 'Inventory',
    'sequence': 25,
    'summary': 'Stock Opening',
    'description': """    
Stock Opening
""",
    'author': 'Seventh Computing',
    'website': 'http://www.7thcomputing.com',
    'depends': ['base', 'stock'],
    'data': [
            'views/stock_opening_view.xml',
            ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
