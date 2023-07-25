{
    'name': 'Product Fast Loading',
    'version': '1.0',
    'category': 'Product',
    'sequence': 30,
    'summary': 'Product',
    'description': """
Product

""",
    'author': 'Seventh Computing',
    'website': 'http://www.7thcomputing.com',
    'depends': ['base','product','mrp','purchase','sale','stock'
    ],
    'data': [
        'views/mrp_view.xml',
        'views/purchase_view.xml',
        'views/sale_view.xml',
        'views/product_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
