{
    'name': 'Payment & Cash Register Link',
    'version': '1.0',
    'category': 'Account',
    'sequence': 25,
    'summary': 'Account Cashbook Customization',
    'description': """
    Account Customization
""",
    'author': 'Seventh Computing',
    'website': 'http://www.7thcomputing.com',
    'depends': ['account','hr_expense'],
    'data': [
             'views/account_bank_statement_view.xml',
             #'views/account_payment_view.xml',
             #'wizard/hr_expense_sheet_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}