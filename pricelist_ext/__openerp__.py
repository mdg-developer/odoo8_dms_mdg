{
    'name': 'Pricelist Ext',
    'version': '1.0',
    'category': 'Pricelist Ext',
    'sequence': 25,
    'summary': '1atest',
    'description': """
Pricelist Ext

""",
    'author': 'Seventh Computing',
    'website': 'http://www.7thcomputing.com',
    'depends': ["base", "product", "product_product","product_pricelists"],
    'data': [
       'views/product_pricelist_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
