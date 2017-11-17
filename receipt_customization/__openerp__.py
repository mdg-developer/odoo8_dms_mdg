{
    'name': 'Receipt Customization',
    'version': '1.0',
    'category': 'Receipt Customization',
    'sequence': 30,
    'summary': 'Receipt Customization',
    'description': """
Customization for Sale Receipt and Purchase Receipt

""",
    'author': 'Seventh Computing',
    'website': 'http://www.7thcomputing.com',
    'depends': ['base','account_voucher','account'
    ],
    'data': [  'view/voucher_sales_purchase_view.xml',      
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
