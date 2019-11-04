{
    'name': 'Partner Google Map',
    'category': 'Hidden',
    'summary': '',
    'version': '1.0',
    'description': """
OpenERP Partner Google Map
==========================

        """,
    'author': 'Seventh Computing',
    'depends': ['website','base_geolocalize','ms_sale_plan_setting'],
    'data': [
        'views/google_map.xml',
        'views/polygon_map_view.xml',
        'views/res_partner.xml',
        'views/sale_plan_day_view.xml',
        'wizard/res_partner_multi_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
