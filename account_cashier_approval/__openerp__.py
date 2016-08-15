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
    'name': 'Sale Cashier Approval',
    'version': '1.0',
    'category': 'Account',
    'sequence': 30,
    'summary': 'Account',
    'description': """
Sale Cashier Approval

""",
    'author': 'Seventh Computing Developer Group',
    'website': 'http://www.7thcomputing.com',
    'depends': ['base','account','account_accountant','ms_mobile_sale_credit','sale_management',                
    ],
    'data': [

       # 'views/product_product_view.xml',
       
         'views/cashier_approval_view.xml',
        'views/qweb_view.xml',
        'views/report_cashier_approval.xml',

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
