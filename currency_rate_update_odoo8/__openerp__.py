# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
    'name': 'Currency Rate Update',
    'version': '1.0',
    'category': 'Currency Rate Update',
    'sequence': 10,
    'summary': 'Currency Rate Update',
    'description': """
Currency Rate Update Module
=================================================
Welcome to Content Management System.
1.Sale Order contain analytic account and currency_rate
2.Purchase Order contain analytic account and currency_rate
3.Division Rate and Multiply Rate in Currency Rate Form
4.Two Type of currencies can work on Journal Entries
    """,
    
    'author': '7th Computing Software Development Team',
    'website': 'http://www.7thcomputing.com',
    'images': [],
    'depends': ['base','account'],
    'data': [
            'currency_rate_update.xml',
            'data/res_currency_data.xml'
            ],
             
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
