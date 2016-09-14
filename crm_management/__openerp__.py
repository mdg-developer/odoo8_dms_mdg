# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'CRM Management',
    'version': '1.0',
    'category': 'CRM',
    'sequence': 30,
    'summary': 'CRM',
    'description': """
CRM Management
Features:
customer code auto generate by city, township, sale channel 
e.g YGN-IS-RETAIN-0001,YGN-IS-RETAIN-0002,

""",
    'author': 'Seventh Computing',
    'website': 'http://www.7thcomputing.com',
    'depends': ['base', 'crm','sale', 'address_management_system', 'crm_class', 'hr_branch', 'crm_demarcation','sale_management', 'crm_sale_channel', 'base_geolocalize', 'crm_partner_assign'
    ],
    'data': [        
        'views/res_partner_view.xml',
        'views/lead_view.xml',
        'views/res_code_view.xml',
        'views/sale_order_configuration.xml',
        'views/res_partner_opportunity.xml',
        'reports/qweb_view.xml',
        'reports/report_crm_management.xml',
        'views/outlet_type_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
