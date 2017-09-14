{
    'name': 'HR Attendance Fingerprint Import MMB',
    'version': '1.0',
    'category': 'HR Finger Print Import',
    'sequence': 14,
    'summary': 'HR Finger Print Attendance file import for attendance record',
    'description': """
HR Finger Print Attendance import Module
=========================================

HR Finger Print Attendance import module will help to import finger print device attendance records to HR Attendance 
records.For import need DAT File format.

    """,
    'author': '7th Computing',
    'website': 'http://www.7thcomputing.com',
    'images': [],
    'depends': ['base','hr_attendance','hr_holidays'],
    'data': [
        'hr_attendance_ext_view.xml',
        'hr_gazetted_holiday_view.xml',
        'hr_attendance_report.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
