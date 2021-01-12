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
    'name': 'Stock Transfer Request',
    'version': '1.1',
    'author': '7th Computing',
    'summary': 'Stock Transfer Request',
    'description': """

Stock Transfer Request' Module
===============================

    """,
    'website': 'https://www.odoo.com/page/warehouse',
    'depends': ['base', 'sale', 'stock'],
    'category': 'stock',
    'sequence': 16,
    'data': [
        'views/sequence.xml',
        'views/stock_transfer_request_view.xml',
        'views/stock_picking_view.xml',
        'reports/mdg_custom_layouts.xml',
        'reports/qweb_view.xml',
        'reports/report_stock_transfer.xml',
    ],
    'test': [

    ],
    
    'installable': True,
}
