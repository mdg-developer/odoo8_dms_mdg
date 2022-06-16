# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today OpenERP SA (<http://www.openerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
    'name': 'Sale FOC And Discount',
    'version': '1.0',
    'sequence': 14,
    'summary': 'Sale FOC And Discount',
    'description': """
Manage your Discount on Account
=========================
With this module for discount making.
    """,
    'author': '7thcomputing developers',
    'website': 'https://www.odoo.com/page/crm',
    'depends': ['account', 'sale', 'account_configuration', 'sale_management'],
    'category': 'Sale , Account',
    'data' : [
        'sale_discount_view.xml',
        'account_invoice_view.xml',
       # 'res_config_view.xml',
        'stock_view.xml',
        'sale_order_view.xml'
    ],
    'demo': [],
    'installable': True,
}
