# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Noviat nv/sa (www.noviat.com). All rights reserved.
#
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
    'name': 'MMB Employee Import',
    'version': '0.1',
    'license': 'AGPL-3',
    'author': 'Phyo Min Zaw',
    'category' : 'Master Data Import',
    'description': """

Import Master Data Entries
=========================

This module will import data  from a EXCEL file.

for following data
 Employee and Contract for employee
    """,
    'depends': ['base','base_import','hr','hr_contract','hr_attendance_ext_MMB'],
    'data' : [
        'data_import_view.xml',
        'uniform_import_view.xml'
    ],
}
