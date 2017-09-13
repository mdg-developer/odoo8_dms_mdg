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
    'name': 'HR Management for MMB',
    'version': '1.0',
    'category': 'MMB HR Management',
    'sequence': 10,
    'summary': 'MMB HR Management',
    
    'description': """
MMBr HR Management Module
=================================================
Welcome to MMB HR Management Module.
    """,
    
    'author': '7th Computing Software Development Team',
    'website': 'http://www.7thcomputing.com',
    'images': [],
    
    'depends': [
                'base',
                'hr',
                'hr_payroll',
                'hr_attendance',
                'hr_holidays',
                'hr_payroll_extension',
                'hr_expense_customise'
                ],
                
    'data': [
              'hr_payroll_view.xml'      ,
              'training_report_view.xml',
              'uniform_report_view.xml',
             # 'wizard/leave_report_view.xml',
             # 'wizard/salaryforssb_view.xml',
              #'wizard/overtime_report_view.xml',
              'incometax_detail_report_view.xml',
              'ssbfee_report_view.xml',
              'hr_contract_view.xml',
              'hr_employee_view.xml',
              'hr_job_view.xml'
              #'wizard/incometax_calculation_view.xml',
              #'wizard/salary_report_view.xml',
              #'wizard/employee_report_view.xml'

             ],
             
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
