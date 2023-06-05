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
    'name': 'Account Credit Note',
    'version': '1.0',
    'category': 'Account Credit Note',
    'sequence': 30,
    'summary': 'Account Credit Note',
    'description': """
Account Credit Note

""",
    'author': 'Seventh Computing',
    'website': 'http://www.7thcomputing.com',
    'depends': ['base','account'
    ],
    'data': [
       'views/account_creditnote_view.xml',
       'views/program_file_view.xml',
       'views/code_sequence.xml',
       'wizard/redeemed_journal_wizard.xml',
       'security/ir.model.access.csv',
       'views/custom_layout.xml',
       'views/report_credit_note.xml',
       'views/qweb_view.xml',
       'views/pricelist_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
