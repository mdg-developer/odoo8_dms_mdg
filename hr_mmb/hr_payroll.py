'''
Created on 2015-03-25'

'''
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
from openerp import models, fields, api, _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DATEFORMAT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as OE_DATETIMEFORMAT
from openerp.tools.translate import _
from openerp.osv import fields, osv
# customization for training  form         

class event_registration(models.Model):
    _inherit = 'event.registration'
    _description = 'Event Registration'
    _columns = {    
    'employee_id' :fields.many2one('hr.employee', string='Employee Name', required=True,
        readonly=True, states={'draft': [('readonly', False)]}),
    'job_id' :fields.many2one('hr.job', string='Job Position', required=True,
        readonly=True, states={'draft': [('readonly', False)]}),
    'exam_remark' :fields.integer("Exam Remark", required=True,
        readonly=True, states={'draft': [('readonly', False)]}),
    'remark' :fields.char("Remark", size=128, required=True,
        readonly=True, states={'draft': [('readonly', False)]}),
                }
    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        emp_obj = self.pool.get('hr.employee')
        department_id = False
        company_id = False
        job_id = False
        email=False
        phone=False
        if employee_id:
            employee = emp_obj.browse(cr, uid, employee_id, context=context)
            department_id = employee.department_id.id
            job_id = employee.job_id.id
            company_id = employee.company_id.id
            email=employee.work_email
            phone=employee.mobile_phone
        return {'value': {'company_id': company_id, 'job_id':job_id,
                          'email': email, 'phone':phone}}
    
# customization for training  form         
class event_event(models.Model):
    _inherit = 'event.event'
    _description = 'Event Event'
    
    def _amount(self, cr, uid, vals, field_name, arg, context=None):
        res= {}
        for fee in self.browse(cr, uid, vals, context=context):
            #print 'fee',fee
            total = 0.0
            h_fee=fee.fee
            other_fee=fee.other_fee
            #print 'fee',h_fee
            #print 'ofee',other_fee
            
            total=h_fee+other_fee
            res[fee.id] = total            
            #print res
        return res
    
    _columns = {    
    'fee' :fields.float("Honorable Fee", readonly=True, states={'draft': [('readonly', False)]}),
    'other_fee' :fields.float("Other Fee", readonly=True, states={'draft': [('readonly', False)]}),
    'amount': fields.function(_amount, string='Total Fee', digits_compute=dp.get_precision('Account')),
    
    'date_begin':fields.datetime('Start Date', required=True),
    'date_end':fields.datetime('End Date', required=True),

    'certificate' :fields.char("Certificate"),
    'status':fields.selection([
                                           ('internal', 'Internal'),
                                           ('external', 'External'),
                                            ], 'Training & Seminar', required=True),
                }
    

    

class last_X_days:

    """Last X Days before resign.
    Keeps track of the days an employee worked/didn't work in the last X days.
    """

    def __init__(self, days=6):
        self.limit = days
        self.arr = []

    def push(self, worked=False):
        if len(self.arr) == self.limit:
            self.arr.pop(0)
        self.arr.append(worked)
        return [v for v in self.arr]

    def days_worked(self):
        res = 0
        for d in self.arr:
            if d == True:
                res += 1
        return res

class hr_payslip_customize(osv.osv):
    '''
    Payslip Worked Time
    '''
    _name = 'hr.payslip'
    _inherit = "hr.payslip"


    def fingerprint_forget(self, cr, uid, contract_ids, date_from, date_to, context=None):
       
        cr.execute('select employee_id from hr_contract where id = %s', (contract_ids))
        employee_id = cr.fetchone()
        # first late
        cr.execute('''select count(AA.sign_in_day) as sign_in_day
               from (
            select  A.att_date::date as sign_in_day,A.employee_id
              from
              (
            select 
            att.name + '6 hour'::interval + '30 minutes'::interval as att_date,att.employee_id
            from hr_attendance att 
            where att.employee_id = %s
            and action='sign_in'
            and att.name+ '6 hour'::interval + '30 minutes'::interval
            between %s and %s
            )A
            )AA
            where AA.sign_in_day not in
            (
            select att_date::date as in_date from(
             select 
            (date_part('hour', cast(to_char(name::timestamp at time zone 'utc', 'yyyy-mm-dd hh24:mi:ss tz') as timestamp)) +
            (((date_part('minute', cast(to_char(name::timestamp at time zone 'utc', 'yyyy-mm-dd hh24:mi:ss tz') as timestamp)))/30)*0.5)) as attendance,att.name + '6 hour'::interval + '30 minutes'::interval as att_date 
            from hr_attendance att 
            where att.employee_id = %s
            and action='sign_out'
            and att.name+ '6 hour'::interval + '30 minutes'::interval
            between %s and %s
            )A
            )''', (employee_id, date_from, date_to , employee_id, date_from, date_to))
        first_data = cr.fetchone()
        #print 'first_data------', first_data
        return first_data[0]
    def get_inputs(self, cr, uid, contract_ids, date_from, date_to, context=None):
        # get job_id
        con_id = len(contract_ids)
        c_id = con_id - 1
        #print 'contract_ids', contract_ids[-c_id]
        contract_ids = contract_ids[-c_id]
        #print 'contract_ids----------', contract_ids
        cr.execute('select job_id from hr_contract where id = %s', (contract_ids,))
        job_id = cr.fetchone()
        # input CLA account
        cr.execute('select cla_amount from hr_job where id = %s', (job_id,))
        cla_amount = cr.fetchone()        

        cr.execute('select employee_id from hr_contract where id = %s', (contract_ids,))
        employee_id = cr.fetchone()
        #half day Leave count
        cr.execute('select count(id) as half_leave from hr_holidays where number_of_days_temp =0.5 and employee_id=%s and date_from::date between %s and %s',(employee_id, date_from, date_to,))
        half_leave=cr.fetchone()
        if half_leave:
            half_leave=half_leave[0]
        else:
            half_leave=0.0
        #sign out Absent
        cr.execute("select count(ha.id) from hr_attendance ha,hr_action_reason hr where hr.id=ha.action_desc and hr.name like '%%Out Absen%%' and ha.employee_id=%s and ha.name::date between %s and %s", (employee_id, date_from, date_to,))
        second_data = cr.fetchone()        
        # fingerprint count sign in absent
        cr.execute('''select count(AA.sign_in_day) as sign_in_day
               from (
            select  A.att_date::date as sign_in_day,A.employee_id
              from
              (
            select 
            att.name + '6 hour'::interval + '30 minutes'::interval as att_date,att.employee_id
            from hr_attendance att 
            where att.employee_id = %s
            and action='sign_out'
            and att.name::date
            between %s and %s
            )A
            )AA
            where AA.sign_in_day not in
            (
            select att_date::date as in_date from(
             select 
            (date_part('hour', cast(to_char(name::timestamp at time zone 'utc', 'yyyy-mm-dd hh24:mi:ss tz') as timestamp)) +
            (((date_part('minute', cast(to_char(name::timestamp at time zone 'utc', 'yyyy-mm-dd hh24:mi:ss tz') as timestamp)))/30)*0.5)) as attendance,att.name + '6 hour'::interval + '30 minutes'::interval as att_date 
            from hr_attendance att 
            where att.employee_id = %s
            and action='sign_in'
            and att.name::date
            between %s and %s
            )A
            )''', (employee_id, date_from, date_to , employee_id, date_from, date_to))
        first_data = cr.fetchone()
        if first_data:
           first_data = first_data[0] * (cla_amount[0] * 2);  
        else:
           first_data = 0.0;  
        if second_data:
           second_data = second_data[0] * (cla_amount[0] * 2);  
        else:
           second_data = 0.0;                     
        late_data=  first_data +  second_data
        res = []
        contract_obj = self.pool.get('hr.contract')
        rule_obj = self.pool.get('hr.salary.rule')

        structure_ids = contract_obj.get_all_structures(cr, uid, contract_ids, context=context)
        rule_ids = self.pool.get('hr.payroll.structure').get_all_rules(cr, uid, structure_ids, context=context)
        sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]



        for contract in contract_obj.browse(cr, uid, contract_ids, context=context):

            #print 'AAAAcontract_ids',contract_ids
            for rule in rule_obj.browse(cr, uid, sorted_rule_ids, context=context):
                if rule.input_ids:
                    for input in rule.input_ids:

#     
                       

                        if input.code == 'CLA':
                           inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':cla_amount[0],
                               'contract_id': contract.id,
                              }
 
                        else:
                            inputs = {
                                     'name': input.name,
                                     'code': input.code,
                                     'amount':0.0,
                                     'contract_id': contract.id,
                                }
                                                                                      
                        if input.code == 'SFF':
                           inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':late_data,
                               'contract_id': contract.id,
                              } 
                        if input.code == 'TAL':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':half_leave,
                               'contract_id': contract.id,
                              }                                                                                                                                                                                                                                
                        res += [inputs]
                        #print 'inputs',res;
            return res

    def _book_restday_hours(
        self, cr, uid, contract, presence_policy, ot_policy, attendances,
            dtDay, rest_days, lsd, worked_hours, context=None):

        done = False
        push_lsd = True
        hours = worked_hours
        # Process normal working hours
        if presence_policy:
            for line in presence_policy.line_ids:
                if line.type == 'restday' and dtDay.weekday() in rest_days:
                    rd_hours = self._get_applied_time(
                        worked_hours, line.active_after, line.duration)
                    attendances[line.code]['number_of_hours'] += rd_hours
                    attendances[line.code]['number_of_days'] += 1.0
                    hours -= rd_hours
                    done = True

        # Process OT hours
        for line in ot_policy.line_ids:
            if line.type == 'restday' and dtDay.weekday() in rest_days:
                ot_hours = self._get_applied_time(
                    worked_hours, line.active_after)
                # get saturaday ot greater than 8 hour
                if(ot_hours >= 8):
                    attendances[line.code]['number_of_hours'] += ot_hours
                    attendances[line.code]['number_of_days'] += 1.0
                    hours -= ot_hours
                    done = True
               

        if done and (dtDay.weekday() in rest_days or lsd.days_worked == 6):
            # Mark this day as *not* worked so that subsequent days
            # are not treated as over-time.
            lsd.push(False)
            push_lsd = False

        if hours > -0.01 and hours < 0.01:
            hours = 0
        return hours, push_lsd                   
       
hr_payslip_customize()

class hr_attendance(osv.osv):
    _inherit = "hr.attendance"
    _columns = {
                'state': fields.selection([
                                           ('draft', 'Not Approved'),
                                           ('approve', 'Approved'),
                                           ], 'Status', readonly=True, copy=False, select=True),
#                 'sign':fields.boolean('Sign Out Forget'),
                }
    def approve(self, cr, uid, ids, context=None):
         return self.write(cr, uid, ids, {'state':'approve'})
     
    def partial_hours_on_day(
        self, cr, uid, contract, dtDay, active_after, begin, stop, morning, tz,
            punches_list=None, context=None):
        #print "In real calculation of partial work hour for other ========================="
      
                                   
        # # begin and stop is already defined in Overtime Policy
        '''Calculate the number of hours worked between begin and stop hours, but
        after active_after hours past the beginning of the first sign-in on specified date.'''

        # Since OpenERP stores datetime in db as UTC, but in naive format we have to do
        # the following to compare our partial time to the time in db:
        #    1. Make our partial time into a naive datetime
        #    2. Localize the naive datetime to the timezone specified by our caller
        #    3. Convert our localized datetime to UTC
        #    4. Convert our UTC datetime back into naive datetime format
        
        # Now we conver then and it values decreases to about 6:30
        dtBegin = datetime.strptime(dtDay.strftime(OE_DATEFORMAT) + ' ' + begin + ':00', OE_DATETIMEFORMAT)
        dtStop = datetime.strptime(dtDay.strftime(OE_DATEFORMAT) + ' ' + stop + ':00', OE_DATETIMEFORMAT)

        if dtStop <= dtBegin:
            dtStop += timedelta(days=1)
        utcdtBegin = timezone(tz).localize(
            dtBegin, is_dst=False).astimezone(utc)
        utcdtStop = timezone(tz).localize(dtStop, is_dst=False).astimezone(utc)
        
        dtBegin = utcdtBegin.replace(tzinfo=None)
        dtStop = utcdtStop.replace(tzinfo=None)

        if punches_list == None:
            punches_list = self.punches_list_init(
                cr, uid, contract.employee_id.id, contract.pps_id,
                dtDay.date(), dtDay.date(), context)
        sin, sout = self._get_normalized_punches(
            cr, uid, contract.employee_id.id, contract.pps_id,
            dtDay.date(), punches_list, context=context)

        worked_hours = 0
        lead_hours = 0
        for i in range(0, len(sin)):
            start = datetime.strptime(sin[i], '%Y-%m-%d %H:%M:%S')
            end = datetime.strptime(sout[i], '%Y-%m-%d %H:%M:%S')
            cr.execute ('select state from hr_attendance where name=%s',(end,))
            state_app=cr.fetchone()
            state=state_app[0]
            if state =='approve':
            # must define end and OT shall end shall be within the boundary
                if morning == False and end and dtStop and end > dtStop:
                        continue;
                    # if signin time is later than configure OT endtime
                if morning == True and start > dtStop:
                        continue;
                
                if worked_hours == 0 and end <= dtBegin:
                    lead_hours += float((end - start).seconds) / 60.0 / 60.0
                elif worked_hours == 0 and end > dtBegin:
                    if morning == False and start < dtBegin:
                        lead_hours += float(
                            (dtBegin - start).seconds) / 60.0 / 60.0
                        start = dtBegin
                    
                    if end > dtStop:
                        end = dtStop
                    worked_hours = float((end - start).seconds) / 60.0 / 60.0
                elif worked_hours > 0 and start < dtStop:
                    if end > dtStop:
                        end = dtStop
                    worked_hours += float((end - start).seconds) / 60.0 / 60.0

                
                
        if worked_hours == 0:
            return 0
        elif lead_hours >= active_after:
            return worked_hours
            #print 'Final work hour is----------', worked_hours
        return max(0, (worked_hours + lead_hours) - active_after)

       
   
hr_attendance()