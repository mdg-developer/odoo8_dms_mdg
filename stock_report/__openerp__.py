{
    'name': 'Stock Reports',
    'version': '8.0',
    'author': (
        "7thcomputing Developers"
    ),
    'category': 'Reporting',
    'website': 'http://www.7thcomputing.com',
    'depends': ['base',
                'stock'],
    'data': [
             'wizard/stock_by_date_wizard_view.xml',
             'report_menus.xml',
             ],
    'active': False,
    'installable': True,
    'application': True,
}
