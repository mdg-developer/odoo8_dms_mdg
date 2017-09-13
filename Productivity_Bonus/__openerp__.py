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
    'name': 'Productivity Bonus',
    'version': '1.0',
    'category': 'Human Resources',
    'sequence': 10,
    'summary': 'Productivity Bonus',
    
    'description': """
Productivity Bonus Module
=================================================
Welcome to Productivity Bonus Module.
    """,
    
    'author': ' 7th Computing Software Development Team',
    'website': 'http://www.7thcomputing.com',
    'images': [],
    
    'depends': [
                'base',
                'hr'
                ],
                
                
    'data' : [
        'week_configuration_view.xml',
        'productivity_bonus_setting.xml',
        'abnormal_employee_setting.xml',
        'employee_performance.xml',
        'emp_bonus_setting.xml',
        'productivity_bonus_entry.xml'
    ],
    'css': ['static/src/css/productivity.css'],    
    'demo': [],
    'installable': True,
    'auto_install': False,
   
}




