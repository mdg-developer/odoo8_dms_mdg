{
    'name': 'Credit Note Import',
    'version': '1.0',
    'category': 'Credit Note Import',
    'sequence': 30,
    'summary': 'Credit Note Import',
    'description': """
This module allows to import credit notes.

""",
    'author': 'Seventh Computing',
    'website': 'http://www.7thcomputing.com',
    'depends': ['base', 'account_creditnote'
    ],
    'data': [        
             'views/credit_note_import_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
