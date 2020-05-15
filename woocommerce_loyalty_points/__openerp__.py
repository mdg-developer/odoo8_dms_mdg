{
    'name' : 'Woocommerce Loyalty Points and Rewards',
    'version' : '1.0',
    'author': 'seventh computing',
    'website': 'http://www.7thcomputing.com',
    'category' : 'Sales',
    'depends' : ['base','sale'],
    'description': """
Woocommerce Loyalty Points and Rewards
    """,
    'data': [
        'views/sale_order_view.xml',
        'views/point_history_view.xml',        
        'views/membership_config_view.xml',        
        'views/res_partner_view.xml',  
	],
    'installable': True,
    'auto_install': False,
}
