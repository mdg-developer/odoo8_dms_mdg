{
    'name': 'Website Landed-cost Tempate',
    'category': 'Website',
    'author': 'seventh computing',
    'summary': 'Send Professional Landed-cost',
    'website': 'http://www.7thcomputing.com',
    'version': '1.0',
    'description': """
OpenERP Sale Quote Roller
=========================

        """,
    'depends': ['website','sale', 'stock_landed_costs'],
    'data': [
        'views/landed_cost_template_view.xml',
        'views/stock_landed_cost_view.xml',
  
    ],


    'installable': True,
}
