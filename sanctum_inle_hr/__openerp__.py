{
    'name': 'HR Management Customization for Sanctum Inle',
    'version': '1.0',
    'category': 'Sanctum Inle HR Management',
    'sequence': 14,
    'summary': 'Sanctum Inle  HR',
    'description': """
Sanctum Inle HR Module
===========================

Sanctum Inle HR Management module.

    """,
    'author': '7th Computing Developer Team',
    'website': 'http://www.7thcomputing.com',
    'images': [],
    'depends': [
                'base',
                'hr',
                'hr_payroll',
                'hr_attendance',
                'hr_holidays',
                'hr_family',
                'hr_holidays_extension'

                ],
    'data': [
          'hr_view.xml',
         #'wizard/payslip_report_view.xml',
        # 'wizard/hr_report_view.xml',
         'account_view.xml',
         'hr_holidays_view.xml',
         'security/hr_security.xml'
     
    ],
    'demo': [
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
}
