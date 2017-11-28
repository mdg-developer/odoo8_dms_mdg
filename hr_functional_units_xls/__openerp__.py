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
###############################################################################

{
    'name': 'HR Functional Units',
    'version': '1.0',
    'category': 'HR Functional Units',
    'sequence': 11,
    'summary': 'HR Functional Units',
    
    'description': """
'HR Functional Units'
=================================================
Welcome to 'HR Functional Units'
    """,
    
    'author': '7th Computing Software Development Team',
    'website': 'http://www.7thcomputing.com',
    'images': ['icons/icon.png'],
    'depends': ['base','hr'],
                    
    'data': [
            
           'hr_functional_units_view.xml',
           'department_view.xml',
           'hr_team_view.xml',
           'hr_business_units_view.xml',
           'hr_mic_view.xml',
           'hr_employee_view.xml'
             ],
             
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
