{
    'name': 'Product Agree Rate',
    'version': '1.1',
    'author': '7th Computing',
    'summary': 'Request Product Agree Rate',
    'description': """

Request Product Agree Rate For  Module
==================================================

    """,
    'website': 'https://www.odoo.com/page/warehouse',
    'depends': ['base','sale','stock'],
    'category': 'stock',
    'sequence': 16,
    'data': [
        'views/product_agree_return_view.xml',
    ],
    'test': [

    ],
    
    'installable': True,
}