{
    'name': 'Automatic Workflow Settings',
    'version': '8.0',
    'license': 'LGPL-3',
    'category': 'Sales',
    'description': """
        
    """,
    'author': 'Emipro Technologies',
    'website': 'http://www.emiprotechnologies.com/',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',
    'depends': ['sale','account'], 
    'init_xml': [],
    'data': [ 
            'view/sale_workflow_process_view.xml',
            'view/automatic_workflow_data.xml',
            'security/ir.model.access.csv',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
    'images': ['static/description/Automatic-Workflow-Cover.jpg']
}

