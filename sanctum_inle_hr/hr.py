# -*- coding:utf-8 -*-
#
#
#    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
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
#

from pytz import timezone, utc

import openerp.addons.decimal_precision as dp
from datetime import datetime, timedelta

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DATEFORMAT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as OE_DATETIMEFORMAT
from openerp.tools.translate import _
from openerp.osv import fields, osv
MONTH_SELECTION = [('1','January'),
            ('2','February'),
            ('3', 'March'),
            ('4','April'),
            ('5 ','May'),
            ('6','June'),
            ('7','July'),
            ('8','August'),
            ('9','September'),
            ('10','October'),
            ('11','November'),
            ('12','December')]
class hr_payslip_customize(osv.osv):
    '''
    Payslip Worked Time
    '''
    _inherit = 'hr.payslip'


    def get_inputs(self, cr, uid, contract_ids, date_from, date_to, context=None):
        #calculate amount for new appointment employee in payslip
        cr.execute('select trial_date_start,wage from hr_contract where id = %s', (contract_ids))
        date= cr.fetchone()
        day_from =datetime.strptime(date_from,"%Y-%m-%d").date()
        print 'day_from1',day_from;
        day_to = datetime.strptime(date_to,"%Y-%m-%d").date()
        print 'day_to1',day_to;

        trial_date_start=datetime.strptime(str(date[0]),"%Y-%m-%d").date()
        print 'trial_date_start1',trial_date_start;

        #month_days =calendar.monthrange(day_from.year, day_from.month)[1]
        #for new appointment employee
        if(str(day_from)<str(trial_date_start)):
            new_date= (trial_date_start-day_from).days;
            new_appointment=((date[1])/30)*new_date;            
        else:   
            new_appointment=0.0;  
        cr.execute('select employee_id from hr_contract where id = %s', (contract_ids))
        employee_id= cr.fetchone()
        res = []
        contract_obj = self.pool.get('hr.contract')
        rule_obj = self.pool.get('hr.salary.rule')

        structure_ids = contract_obj.get_all_structures(cr, uid, contract_ids, context=context)
        rule_ids = self.pool.get('hr.payroll.structure').get_all_rules(cr, uid, structure_ids, context=context)
        sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]

        for contract in contract_obj.browse(cr, uid, contract_ids, context=context):
            for rule in rule_obj.browse(cr, uid, sorted_rule_ids, context=context):
                if rule.input_ids:
                    for input in rule.input_ids:

                        if input.code == 'LD100':
                           inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':0,
                               'contract_id': contract.id,
                              }
 
                        else:
                            inputs = {
                                     'name': input.name,
                                     'code': input.code,
                                     'contract_id': contract.id,
                                }
                        if input.code == 'PB100':
                           inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':0,
                               'contract_id': contract.id,
                              }
    
                        if input.code == 'NAD':
                           inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':new_appointment,
                               'contract_id': contract.id,
                              }
 
                        else:
                            inputs = {
                                     'name': input.name,
                                     'code': input.code,
                                     'contract_id': contract.id,
                                }                                                           
                        res += [inputs]
            return res     
        
        
          
class hr_contract(osv.osv):
    _inherit = 'hr.contract'
    _description = 'Contract'
    _columns = {
                'tax_wage': fields.float('Tax Wage', digits=(16, 2), required=True),
                }
hr_contract()  



class hr_employee(osv.osv):

    _inherit = 'hr.employee'
                                
#     def __init__(self):
#         self.cr.execute('update hr_employee set month=Extract(month from birthday)')
        
    def _calculate_age(self, cr, uid, ids, field_name, arg, context=None):

        res = dict.fromkeys(ids, False)
        for ee in self.browse(cr, uid, ids, context=context):
            if ee.birthday:
                dBday = datetime.strptime(ee.birthday, OE_DATEFORMAT).date()
                dToday = datetime.now().date()
                res[ee.id] = (dToday - dBday).days / 365
                print 'dBday---',dBday
                cr.execute('update hr_employee set month=Extract(month from %s) where id=%s',(dBday,ee.id,))                
        return res  
    
    _columns = {
        'age': fields.function(_calculate_age, type='integer', method=True, string='Age'),
                
        'month':fields.selection(MONTH_SELECTION,'Birthday Month'),
 'is_fam_father':fields.boolean('Is Stay With Together'),
                'is_fam_mother':fields.boolean('Is Stay With Together'),
                 'f_name':fields.char("Father-In-Law's Name"),
                'is_father_inlaw':fields.boolean('Is Stay With Father-In-Law'),
                  'm_name':fields.char("Mother-In-Law's Name"),

                'is_mother_inlaw':fields.boolean('Is Stay With Mother-In-Law'),
           'education_id': fields.many2one('hr.recruitment.degree', "Education"),
           'working_exp':fields.char('Working Experience', size=50),
           'other':fields.text('Other qualification', size=50),                
        } 
    _defaults = {
        'is_father_inlaw': False,
        'is_mother_inlaw':False,
        }
  




     


    
    
    
