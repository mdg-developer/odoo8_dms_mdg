# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

{
    'name': 'Theme Crafito',
    'summary': 'Advanced Responsive Theme with A Range of Custom Snippets',
    'description': '''Theme Crafito
Business theme
Hardware theme
Hardware and tools theme
Single Page theme
Digital security theme
Event theme
Medical equipments theme
''',
    'category': 'Theme/Ecommerce',
    'version': '8.0.1.0.7',
    'author': 'AppJetty',
    'website': 'https://goo.gl/Qy5mrR',
    'depends': [
        'website_less',
        'website_hr',
        'mass_mailing',
        'website_sale',
        'website_blog',
        'website_event_sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/views.xml',
        'views/website_view.xml',
        'views/slider_views.xml',
        'views/snippets.xml',
        'views/theme_customize.xml',
        'views/theme.xml',
    ],
    'demo': [
        # 'demo/demo_homepage.xml',
    ],
    'support': 'support@appjetty.com',
    'live_test_url': 'http://theme-crafito.appjetty.com/',
    'images': ['static/description/splash-screen.png'],
    'application': True,
    'price': 149.00,
    'currency': 'EUR',
}
