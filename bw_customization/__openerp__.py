{
    'name': 'BW Customization',
    'version': '1.0',
    'category': 'BW Customization',
    'sequence': 25,
    'summary': 'BW Customization',
    'description': """
BW Customization

""",
    'author': 'Seventh Computing',
    'website': 'http://www.7thcomputing.com',
    'depends': ['base', 'product', 'purchase_requisition'],
    'data': [

       'views/product_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
