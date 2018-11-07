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
    'name': 'OT Approval V2',
    'version': '1.0',
    'category': 'HR',
    'sequence': 25,
    'summary': 'OT Approval V2',
    'description': """
HR Section

""",
    'author': 'Seventh Computing',
    'website': 'http://www.7thcomputing.com',
    'depends': ['base',      
        'hr','attendance_data_import_v2'
 
    ],
    'data': [
       'views/report_ot_form.xml',
       'views/ot_approval_view.xml',
       'views/ot_custom_layouts.xml',
       'views/ot_report.xml',
       'wizard/ot_make_approve_view.xml',
       'wizard/ot_make_decline_view.xml',
       'wizard/hr_holidays_approve_view.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
}