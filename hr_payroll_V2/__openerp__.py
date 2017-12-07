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
    'name': 'HR Payroll Version 2',
    'version': '1.0',
    'category': 'HR Payroll Version 2',
    'sequence': 10,
    'summary': 'HR Payroll Version 2',
    
    'description': """
HR Payroll Version 2 Module
=================================================
Welcome to HR Management Module.
    """,
    
    'author': '7th Computing Software Development Team',
    'website': 'http://www.7thcomputing.com',
    'images': [],
    
    'depends': [
                'base',
                'hr',
                'hr_contract',
                'hr_fine',
                'hr_section',
                'hr_employee_id_fingerprint_id',
                'hr_employee_state',
                'hr_payroll',
                'hr_holidays',
                'attendance_data_import_v2'
                ],
                
    'data': [
            'hr_contract_view.xml',

            'hr_payroll_view.xml',
             ],
             
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
