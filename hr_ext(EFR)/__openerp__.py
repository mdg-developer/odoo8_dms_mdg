{
    'name': 'HR Extension',
    'version': '1.0',
    'category': 'HR Ext Import',
    'sequence': 14,
    'summary': 'HR Ext',
    'description': """
HR Finger Print Attendance import Module
=================================================

HR Finger Print Attendance import module will help to import finger print device attendance records to HR Attendance 
records.

    """,
    'author': '7th Computing',
    'website': 'http://www.7thcomputing.com',
    'images': [],
    'depends': ['base','hr','hr_holidays'],
    'data': [
        'hr_ext_view.xml'
    ],
    'demo': [
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
