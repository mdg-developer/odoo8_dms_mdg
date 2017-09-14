{
    'name': 'HR Employee id and Finger print id',
    'version': '0.1',
    'author': '7thcomputing Developer Group',
    'category' : 'HR Employee id and Finger print id',
    'depends': ['base','hr','hr_recruitment'],
    'summary': 'HR Employee id and Finger print id',
    'description': """
HR Employee id and Finger print id

""",

    'data' : [
        'views/exployee_prefix_view.xml',      
        'views/hr_fp_view.xml',
        
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

