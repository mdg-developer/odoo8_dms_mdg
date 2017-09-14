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
    'name': 'Temporary Out Data Import',
    'version': '0.1',
    'license': 'AGPL-3',
    'author': '7th Computing',
    'category' : 'Temporary Out  Data Import',
    'description': """

Import Temporary Out  Data Entries
=========================

This module will import data  from a EXCEL file.

for following data
 Sale Incentive for employee
    """,
    'depends': ['base','base_import','hr','hr_contract'],
    'data' : [
        'data_import_view.xml'
        
    ],
}
