{
    'name': 'HR Beauty World',
    'version': '1.0',
    'category': 'HR',
    'sequence': 14,
    'summary': 'HR Beauty World',
    'description': """
Beauty World HR Module
=======================


    """,
    'author': '7th Computing',
    'website': 'http://www.7thcomputing.com',
    'images': [],
    'depends': ['base','hr','hr_contract','hr_payroll'],
    #'css':'static/src/style1.css',
    'data': [
        'views/hr_employee_view.xml',
        'views/hr_contract_view.xml',
        'views/hr_payroll_view.xml',
        
    ],
    'demo': [
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}