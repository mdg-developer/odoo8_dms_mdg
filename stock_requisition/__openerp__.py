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
    'name': 'Request For Issue And Good Issue Note',
    'version': '1.1',
    'author': '7th Computing',
    'summary': 'Request For Issue And Good Issue Note',
    'description': """

Request For Issue And Good Issue Note Module
=========================

    """,
    'website': 'https://www.odoo.com/page/warehouse',
    'depends': ['base','sale','stock'],
    'category': 'stock',
    'sequence': 16,
    'data': [
        'views/product_requisition_sequence.xml',
        'views/stock_request_view.xml',
        'views/good_issue_note_view.xml',
        'views/stock_return_view.xml',
        'views/stock_return_for_mobile_view.xml',
        'views/good_issue_note_tr_view.xml',
        'views/request_for_issue_view.xml',
        'reports/qweb_view.xml',
        'reports/report_good_issue_note.xml',
        'reports/report_stock_request.xml',
		'reports/srn_qweb_view.xml',
        'reports/stock_return_note.xml',
    ],
    'test': [

    ],
    
    'installable': True,
}
