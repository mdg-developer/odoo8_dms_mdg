{
    'name': 'HR Customization',
    'version': '1.0',
    'category': 'HR',
    'sequence': 14,
    'summary': 'HR Customization                                        ',
    'description': """
HR Customization Module
=======================
Auto Reject in HR Recruitment

    """,
    'author': '7th Computing',
    'website': 'http://www.7thcomputing.com',
    'images': [],
    'depends': ['base','hr','hr_employee_seniority','hr_recruitment','nrc_information','hr_employee_state'],
    #'css':'static/src/style1.css',
    'data': [
        'views/hr_recruitment_view.xml',
        #'views/hr_nrc_prefix_view.xml',
        'views/hr_employee_view.xml',
        'views/hr_contract_view.xml',
        'reports/custom_layout.xml',
        #'reports/contract_layout.xml',
        'reports/employee_paper_format.xml',
        'reports/qweb_view.xml',
        'reports/report_employee_card.xml',
        'reports/report_employee_contract.xml',
       
    ],
    'demo': [
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
