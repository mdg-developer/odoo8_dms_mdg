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
    'name': 'Addidas HR',
    'version': '1.0',
    'category': 'Human Resources',
    'sequence': 10,
    'summary': 'Addidas Human Resources',
    
    'description': """
Addidas HR Module
=================================================
Welcome to Addidas HR Module.
    """,
    
    'author': ' 7th Computing Software Development Team',
    'website': 'http://www.7thcomputing.com',
    'images': [],
    
    'depends': [
                'base',
                'hr',
                'hr_payroll',
                'hr_attendance',
                'hr_holidays',
                'hr_employee_education',
                'hr_payroll_extension',
                'hr_expense_customise'
                ],
                
                
    'data' : [
        'bonus_setting.xml',
        'hr_employee_view.xml',
        'seniority_view.xml',
        'bonus_entry_view.xml'
#         'productivity_bonus_setting.xml',
#         'abnormal_employee_setting.xml',
#         'employee_performance.xml',
#         'res_config_view.xml',
#         'productivity_bonus_entry.xml',
#         'week_configuration_view.xml',
        
    ],
             
    'demo': [],
    'installable': True,
    'auto_install': False,
   
}




