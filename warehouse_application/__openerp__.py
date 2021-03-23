{
    'name' : 'Warehouse Application',
    'version' : '1.0',
    'author': 'seventh computing',
    'website': 'http://www.7thcomputing.com',
    'category' : 'Sales',
    'depends' : ['base','branch_inventory_transfer','product'],
    'description': """
Warehouse Application
    """,
    'data': [
        'views/res_branch_view.xml',
        'views/product_view.xml',
	],
    'installable': True,
    'auto_install': False,
}
