{
    'name': 'Product Quantity Limit',
    'version': '1.0',
    'author': '',
    'website': '',
    'category': 'Sales',
    'depends': ["base", "sale", "product",],
    'description': """
    Product for OpenERP
    = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =



    """,
    'data': [
        'security/ir.model.access.csv',
        'views/product_limit_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: