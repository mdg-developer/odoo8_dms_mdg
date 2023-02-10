{
    'name': 'CRM Unverify Customer Location',
    'version': '1.0',
    'category': 'CRM',
    'sequence': 30,
    'summary': 'CRM',
    'description': """
CRM Management
Features:
Unverify customer location

""",
    'author': 'Seventh Computing',
    'website': 'http://www.7thcomputing.com',
    'depends': ['base_geolocalize'],
    'data': [
        'views/res_partner_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
