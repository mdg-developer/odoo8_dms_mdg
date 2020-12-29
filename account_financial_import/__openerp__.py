{
    'name': 'Account Financial Report Import',
    'version': '0.1',
    'license': 'AGPL-3',
    'author': '7thcomputing',
    'category' : 'Account Financial Report Import',
    'description': """

Account Financial Report Import
===========================

This module will import data  from a XLS file.

for following data
account financial reports
    """,
    'depends': ['base','base_import'],
    'data' : [
        'data_import_view.xml',
    ],
        'installable': True,
    'auto_install': False,
}