{
    'name': 'Product OOS Form',
    'version': '1.0',
    'author': '',
    'website': '',
    'category': 'Sales',
    'depends': ["base", "sale", "product","woo_commerce_ept",],
    'description': """
    Product for OpenERP
    = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =



    """,
    'data': [
        'security/ir.model.access.csv',
        'views/product_oos.xml',
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: