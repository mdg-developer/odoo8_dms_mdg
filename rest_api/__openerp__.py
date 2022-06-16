# -*- coding: utf-8 -*-
{
    'name': 'Professional REST API',
    'version': '8.0.1.9.2',
    'category': 'API',
    'author': 'Andrey Sinyanskiy SP',
    'support': 'avs3.ua@gmail.com',
    'license': 'Other proprietary',
    'price': 129.00,
    'currency': 'EUR',
    'summary': 'Professional RESTful API access to Odoo models with predefined and tree-like schema of response Odoo fields',
    'shortdesc': """
This module provide professional RESTful API (json) access to Odoo models with predefined and tree-like schema of response Odoo fields.
""",
    'live_test_url': 'https://rest-api-demo.dsdatacloud.de/web/login',
    'external_dependencies': {
        'python': ['simplejson'],
    },
    'depends': [
        'base',
        'web',
        'sale_promotions'
    ],
    'data': [
        'data/ir_configparameter_data.xml',
        'data/ir_cron_data.xml',
        'security/ir.model.access.csv',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
