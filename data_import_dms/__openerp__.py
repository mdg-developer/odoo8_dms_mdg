# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Noviat nv/sa (www.noviat.com). All rights reserved.
# r
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Distribution Management System Data Import',
    'version': '0.1',
    'license': 'AGPL-3',
    'author': '7thcomputing Developer Group',
    'category' : 'Master Data Import',
    'description': """

Import Master Data Entries
=========================

This module will import data  from a EXCEL file.

for following data
 Product ,Customer, Sale Order
    """,
    'depends': ['base', 'base_import', 'stock', 'address_management_system'],
    'data' : [

              'views/data_import_view.xml',
              'views/sale_plans_import_view.xml',
              'views/stock_move_import_view.xml',
              'views/hr_employee_import_view.xml',
              'views/price_list_view.xml',
              'wizard/pricelist_import_view.xml'
    ],
}
