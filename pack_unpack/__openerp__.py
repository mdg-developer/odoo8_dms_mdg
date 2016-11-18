{
    'name': 'Products Pack Unpack',
    'version': '1.0',
    'category': 'Products Management',
    'sequence': 14,
    'summary': 'Products',
    'description': """
Product Pack Unpack Module
===========================================================================

Products Management module.

    """,
    'author': '7th Computing',
    'website': 'http://www.7thcomputing.com',
    'images': [],
    'depends': ['stock'
                ],
    'data': [
             'wizard/pack_product_produce_view.xml',
             'wizard/unpack_product_produce_view.xml',
             'wizard/change_production_quantity_view.xml',
             'wizard/stock_move_view.xml',
             'pack_unpack_view.xml',
             'unpack_pack_view.xml',
             'product_view.xml',
           #  'bom_product_view.xml',
             'pack_workflow.xml',
             'unpack_workflow.xml',
             'pack_data.xml',
             'stock_view.xml'
             
            ],
    'demo': [
    ],
    'test': [],
    'css': ['static/src/css/account.css'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
