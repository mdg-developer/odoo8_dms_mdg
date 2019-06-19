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
    'name': 'Branch Inventory Transfer',
    'version': '1.1',
    'author': '7th Computing',
    'summary': 'Branch Inventory Transfer',
    'description': """

Branch Inventory Transfer Module
==================================================

    """,
    'website': 'https://www.odoo.com/page/warehouse',
    'depends': ['base', 'sale', 'stock'],
    'category': 'stock',
    'sequence': 16,
    'data': [
        'views/product_requisition_sequence.xml',
        'views/stock_request_view.xml',
        'views/product_view.xml',
        'views/transport_route_view.xml',
        'views/fleet_view.xml',
        'views/branch_good_issue_note_view.xml',
        'views/branch_view.xml',
        'reports/qweb_view.xml',
        'reports/report_branch_request_issue.xml',
        'reports/report_issue_note.xml',
        'reports/report_receive_note.xml',
        'reports/report_branch_request_loose.xml',
    ],
    'test': [

    ],
    
    'installable': True,
}
