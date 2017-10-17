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
    'depends': ['base', 'product','purchase'],
    'data': [

       'views/product_view.xml',
       'views/purchase_requisitions_view.xml',
       'views/purchase_requisitions_sequence.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
