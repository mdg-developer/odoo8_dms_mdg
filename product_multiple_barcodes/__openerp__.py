{
    'name' : 'Product Multiple Barcodes',
    'version' : '1.0',
    'author': 'seventh computing',
    'website': 'http://www.7thcomputing.com',
    'category' : 'Product',
    'depends' : ["base", "product", "product_product"],
    'description': """
    Product Multiple Barcode
    """,
    'data': [
             'views/product_view.xml',
             'views/product_info_view.xml',
             'security/ir.model.access.csv',
            ],
    'installable': True,
    'auto_install': False,
}

