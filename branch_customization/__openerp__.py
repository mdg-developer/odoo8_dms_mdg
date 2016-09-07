# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
#    Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

{
    'name' : 'Branch Customization',
    'version' : '1.0',
    'author': 'seventh computing',
    'website': 'http://www.7thcomputing.com',
    'category' : 'Reporting',
    'depends' : ["base","sale","account","hr","purchase","sale_management","ms_exchange","stock_requisition"],
    'description': """
Branch Customization    
= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    Features:
    1. Branch Fields All Master Table
    """,
    'data': [
        'views/res_users_view.xml', 
         'views/sale_order_view.xml',
         'views/sale_rental_view.xml',
         'views/sale_denomination_view.xml',
         'views/sale_approval_view.xml',
         'views/sale_return_view.xml',
         'views/hr_view.xml',
         'views/location_view.xml',
         'views/warehouse_ext_view.xml',
         'views/account_ext_view.xml'
                ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: