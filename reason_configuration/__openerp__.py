{
    'name': 'Reason Configuration',
    'version': '1.0',
    'category': 'Sales',
    'sequence': 25,
    'summary': 'Reason Configuration',
    'description': """    
    Reason Configuration
""",
    'author': 'Seventh Computing',
    'website': 'http://www.7thcomputing.com',
    'depends': ['base', 'sale'],
    'data': [
                'views/revise_reason_view.xml',
                'views/cancel_reason_view.xml',
            ],
    'installable': True,
    'auto_install': False,
    'application': True,
}