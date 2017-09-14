{
    'name' : 'Organizational chart',
    'version': '1.0',
    'summary': 'Hierarchy Structure of Companys Employee',
    'category': 'Tools',
    'data': [
        "views/templates.xml",
        "org_chart.xml",
    ],
    'depends' : ['hr'],
    'qweb': ['static/src/xml/*.xml'],
    'application': True,
}
