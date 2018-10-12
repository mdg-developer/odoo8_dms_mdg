
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from openerp import api, tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import calendar
from openerp.tools.safe_eval import safe_eval as eval
from dateutil import parser
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

class hr_payslip_worked_days(osv.osv):
    '''
    Payslip Worked Days
    '''
    _inherit = 'hr.payslip.worked_days'
    _description = 'Payslip Worked Days'
    _columns = {  
        'total_month_day': fields.float('Total Month Days'),
        'total_no_of_days': fields.float('Total Number of Days'),
        'working_month': fields.float('Working Month'),
        'real_working_month': fields.float('Real Working Month'),
        'age_for_ssb': fields.integer('Age for SSB')
        }  
    
class hr_payslip_customize(osv.osv):
    '''
    Payslip Worked Time
    '''
    _inherit = 'hr.payslip'
    _columns = {  
        'total_month_day': fields.float('Total Month Days'),
        'total_no_of_days': fields.float('Total Number of Days'),
        'working_month': fields.float('Working Month'),
        'real_working_month': fields.float('Real Working Month'),
        'branch_id':fields.many2one('res.branch','Branch'),
        'department_id':fields.many2one('hr.department','Department'),
        'badge_id': fields.char('Badge ID'),
        'remark1':fields.text('Remark1'),
        'remark2':fields.text('Remark2')
        
        }
    
    def onchange_employee_id(self, cr, uid, ids, date_from, date_to, employee_id=False, contract_id=False, context=None):
        empolyee_obj = self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')
        worked_days_obj = self.pool.get('hr.payslip.worked_days')
        input_obj = self.pool.get('hr.payslip.input')

        if context is None:
            context = {}
        #delete old worked days lines
        old_worked_days_ids = ids and worked_days_obj.search(cr, uid, [('payslip_id', '=', ids[0])], context=context) or False
        if old_worked_days_ids:
            worked_days_obj.unlink(cr, uid, old_worked_days_ids, context=context)

        #delete old input lines
        old_input_ids = ids and input_obj.search(cr, uid, [('payslip_id', '=', ids[0])], context=context) or False
        if old_input_ids:
            input_obj.unlink(cr, uid, old_input_ids, context=context)


        #defaults
        res = {'value':{
                      'line_ids':[],
                      'input_line_ids': [],
                      'worked_days_line_ids': [],
                      #'details_by_salary_head':[], TODO put me back
                      'name':'',
                      'contract_id': False,
                      'struct_id': False,
                      'badge_id': False,
                      }
            }
        if (not employee_id) or (not date_from) or (not date_to):
            return res
        ttyme = datetime.fromtimestamp(time.mktime(time.strptime(date_to, "%Y-%m-%d")))
        employee_id = empolyee_obj.browse(cr, uid, employee_id, context=context)
        res['value'].update({
                    'name': _('Salary Slip of %s for %s') % (employee_id.name, tools.ustr(ttyme.strftime('%B-%Y'))),
                    'company_id': employee_id.company_id.id,
                    'badge_id': employee_id.employee_id
        })

        if not context.get('contract', False):
            #fill with the first contract of the employee
            contract_ids = self.get_contract(cr, uid, employee_id, date_from, date_to, context=context)
        else:
            if contract_id:
                #set the list of contract for which the input have to be filled
                contract_ids = [contract_id]
            else:
                #if we don't give the contract, then the input to fill should be for all current contracts of the employee
                contract_ids = self.get_contract(cr, uid, employee_id, date_from, date_to, context=context)

        if not contract_ids:
            return res
        contract_record = contract_obj.browse(cr, uid, contract_ids[0], context=context)
        res['value'].update({
                    'contract_id': contract_record and contract_record.id or False
        })
        struct_record = contract_record and contract_record.struct_id or False
        if not struct_record:
            return res
        res['value'].update({
                    'struct_id': struct_record.id,
        })
        #computation of the salary input
        worked_days_line_ids = self.get_worked_day_lines(cr, uid, contract_ids, date_from, date_to, context=context)
        input_line_ids = self.get_inputs(cr, uid, contract_ids, date_from, date_to, context=context)
        res['value'].update({
                    'worked_days_line_ids': worked_days_line_ids,
                    'input_line_ids': input_line_ids,
        })
        return res
    
    def get_inputs(self, cr, uid, contract_ids, date_from, date_to, context=None):
        res = []
        contract_obj = self.pool.get('hr.contract')
        emloyee_obj = self.pool.get('hr.employee')
        rule_obj = self.pool.get('hr.salary.rule')
        financial_year = 0
        total_income = 0
        tax_paid = 0   
        payroll_total_income = 0
        income_tax = 0
        # get Contract data
        cr.execute("select employee_id,date_start,date_end,state,effective_date from hr_contract where id=%s", (contract_ids))
        contract_data = cr.fetchone()
        employee_id = contract_data[0]
        initial_date =contract_data[1]
        termination_date = contract_data[2]
        con_state = contract_data[3]
        effective_date = contract_data[4]
        
        #get Employee Data
        cr.execute("""select id,initial_employment_date from hr_employee where id=%s""",(employee_id,))
        emp_data = cr.fetchone()
        if emp_data:
            initial_employment_date = emp_data[1]
        cr.execute("select fiscalyear_id from account_period where date_start <=%s and date_stop >= %s", (date_from, date_to,))
        fiscalyear_id = cr.fetchone()
        if fiscalyear_id:
            fiscalyear_id = fiscalyear_id[0]
            cr.execute("select financial_year,total_income,tax_paid  from hr_employee he ,account_period ap where ap.id=%s and he.id=%s", (fiscalyear_id, employee_id,))
            previous_tax = cr.fetchone()
            if previous_tax:
                financial_year = previous_tax[0]
                total_income = previous_tax[1]
                tax_paid = previous_tax[2]
            cr.execute ("select sum(hpl.total) as total_income from hr_payslip h , hr_payslip_line hpl ,(select date_start,date_stop from account_period where fiscalyear_id = %s) f where hpl.slip_id =h.id and h.date_from=f.date_start and h.date_to=f.date_stop and state ='done'and code = 'NET'  and h.employee_id=%s ", (fiscalyear_id, employee_id,))    
            payroll_total_income = cr.fetchone()
            if payroll_total_income:
                payroll_total_income = payroll_total_income[0]      
            cr.execute ("select sum(hpl.total) as income_tax from hr_payslip h , hr_payslip_line hpl ,(select date_start,date_stop from account_period where fiscalyear_id = %s) f where hpl.slip_id =h.id and h.date_from=f.date_start and h.date_to=f.date_stop and state ='done'and code = 'ICT'  and h.employee_id=%s ", (fiscalyear_id, employee_id,))             
            income_tax = cr.fetchone()
            if income_tax:
                income_tax = income_tax[0]      
        structure_ids = contract_obj.get_all_structures(cr, uid, contract_ids, context=context)
        rule_ids = self.pool.get('hr.payroll.structure').get_all_rules(cr, uid, structure_ids, context=context)
        sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]
        if initial_employment_date and date_to:
            service_start_date = datetime.strptime(
                    initial_employment_date, '%Y-%m-%d').date()
            service_end_date = datetime.strptime(
                    date_from, '%Y-%m-%d').date()
            service_year = relativedelta(service_end_date, service_start_date)
            service_bonus=0.0
            if service_year.years>= 1:
                cr.execute("""select service_bonus from hr_contract where id=%s""",(contract_ids))
                service_data=cr.fetchone()
                if service_data:
                    service_bonus=service_data[0]
        cr.execute("""select sum(fine_amount) from hr_fine where lost_date between %s and %s
            and employee_id= %s and reason_id in (select id from hr_fine_reason where upper(code) not in ('DPS','UCL','LON','SSB'))""", (date_from, date_to, employee_id,))
        fine_data = cr.fetchone()
        if fine_data:
            fine_amount = fine_data[0]
        else:
            fine_amount = 0.0
        cr.execute("""select sum(fine_amount) from hr_fine where lost_date between %s and %s
            and employee_id= %s and reason_id in (select id from hr_fine_reason where upper(code) in ('SSB'))""", (date_from, date_to, employee_id,))
        ssb_data = cr.fetchone()
        if ssb_data:
            ssb_amount = ssb_data[0]
        else:
            ssb_amount = 0.0
        cr.execute("""select sum(fine_amount) from hr_fine where lost_date between %s and %s
            and employee_id= %s and reason_id in (select id from hr_fine_reason where upper(code) in ('DPS'))""", (date_from, date_to, employee_id,))
        deposit_data = cr.fetchone()
        if deposit_data:
            deposit_amount = deposit_data[0]
        else:
            deposit_amount = 0.0
        cr.execute("""select sum(fine_amount) from hr_fine where lost_date between %s and %s
            and employee_id= %s and reason_id in (select id from hr_fine_reason where upper(code) in ('UCL'))""", (date_from, date_to, employee_id,))
        claim_data = cr.fetchone()
        if claim_data:
            claim_amount = claim_data[0]
        else:
            claim_amount = 0.0
        cr.execute("""select sum(fine_amount) from hr_fine where lost_date between %s and %s
            and employee_id= %s and reason_id in (select id from hr_fine_reason where upper(code) in ('LON'))""", (date_from, date_to, employee_id,))
        loan_data = cr.fetchone()
        if loan_data:
            loan_amount = loan_data[0]
        else:
            loan_amount = 0.0
        cr.execute("""select count(*) from hr_holidays where date_from >= date_from and date_to <= date_to and 
            employee_id =%s and holiday_status_id in (select id from hr_holidays_status where name='Trip_Leave')""", (employee_id,))
        trip_data = cr.fetchone()
        if trip_data:
            trip_amount = trip_data[0]
        else:
            trip_amount = 0.0
        cr.execute("""select count(late)  from attendance_data_import where date between %s and  %s
                and late > 15 and employee_id=%s""", (date_from,date_to,employee_id,))
        late_data = cr.fetchone()
        if late_data:
            late_count = late_data[0]
        else:
            late_count = 0.0
        cr.execute("""select count(early)  from attendance_data_import where date between %s and  %s
                and early > 15 and employee_id=%s""", (date_from,date_to,employee_id,))
        early_data = cr.fetchone()
        if early_data:
            early_count = early_data[0]
        else:
            early_count = 0.0
        cr.execute("""select (punch_in+punch_out) as punch_count from 
        (select count(miss_punch_in) as punch_in,count(miss_punch_out) as punch_out from attendance_data_import where date between %s and  %s
        and (miss_punch_in = True or miss_punch_out = True) and employee_id=%s)A""", (date_from,date_to,employee_id,))
        misspunch_data = cr.fetchone()
        if misspunch_data:
            misspunch_count = misspunch_data[0]
        else:
            misspunch_count = 0.0
        cr.execute("select sum(early) as early_time ,sum(late) as late_min  from attendance_data_import where date between %s and  %s and  employee_id=%s", (date_from, date_to,employee_id,))
        total_minus = cr.fetchone()    
        if total_minus:
            early_minus = total_minus[0]
            late_min = total_minus[1]
        else:
            early_minus = 0
            late_min = 0         
        cr.execute("""select COALESCE( sum(ot_time),0) as ot_time,count(date)  from attendance_data_import where 
        date >= %s and date <= %s and date not in (SELECT the_day ::date FROM  generate_series(%s::date, %s ::date, '1 day') d(the_day) 
        WHERE  extract('ISODOW' FROM the_day)= 7) and date not in (select date from hr_holidays_public_line where date >= %s and date <= %s)
        and ot_time>0 and employee_id=%s and state='approve'""", (date_from, date_to,date_from,date_to,date_from,date_to,employee_id,))
        total_ot = cr.fetchone()   
        if total_ot:
            ot_minus = total_ot[0]
            ot_day_count = total_ot[1]
        else:
            ot_minus = 0
            ot_day_count = 0
        cr.execute("""select COALESCE( sum(ot_time),0) as ot_time,count(date)  from attendance_data_import where 
        date >= %s and date <= %s and (date in (SELECT the_day ::date FROM  generate_series(%s::date, %s ::date, '1 day') d(the_day) 
        WHERE  extract('ISODOW' FROM the_day)= 7) or date in (select date from hr_holidays_public_line where date >= %s and date <= %s))
        and ot_time>0 and employee_id=%s and state='approve'""", (date_from, date_to,date_from,date_to,date_from,date_to,employee_id,))
        sun_holiday_ot = cr.fetchone()   
        if sun_holiday_ot:
            sun_holiday_ot_min = sun_holiday_ot[0]
            sun_holiday_ot_day = sun_holiday_ot[1]
        else:
            sun_holiday_ot_min = 0
        cr.execute("""select count(*)*4 from attendance_data_import where 
            --timetable in (select id from shift_timetable where upper(shift_name) !='OT') and
             absent='false' and ot_time = 0 and date between %s and  %s and  employee_id=%s""", (date_from, date_to,employee_id,))
        actual_working_data = cr.fetchone()
        if actual_working_data:
            actual_working_hour = actual_working_data[0]
        else:
            actual_working_hour = 0
        if initial_employment_date >= date_from and termination_date >= date_to:
            cr.execute("""select COALESCE( sum(normal),0) as normal  from attendance_data_import where 
            date >= %s and date <= %s and date not in (SELECT the_day ::date FROM  generate_series(%s::date, %s  ::date, '1 day') d(the_day) 
            WHERE  extract('ISODOW' FROM the_day)= 7)
            and date not in (select date from hr_holidays_public_line where date >= %s and date <= %s)
            and date not in (select generate_series(hh.date_from::date, hh.date_to::date, '1 day')::date as date from hr_holidays hh,hr_holidays_status ss  where hh.holiday_status_id = ss.id and hh.type='remove' and hh.employee_id =%s and hh.date_to >= %s and hh.date_to <= hh.date_to)
            and absent =true and employee_id=%s""",(initial_employment_date, date_to,initial_employment_date, date_to,initial_employment_date, date_to,employee_id,initial_employment_date,employee_id,))
            absent_data =cr.fetchone()
            if absent_data:
                absent_count=absent_data[0]
        
        elif initial_employment_date <= date_from and termination_date <= date_to:
            cr.execute("""select COALESCE( sum(normal),0) as normal  from attendance_data_import where 
            date >= %s and date <= %s and date not in (SELECT the_day ::date FROM  generate_series(%s::date, %s  ::date, '1 day') d(the_day) 
            WHERE  extract('ISODOW' FROM the_day)= 7)
            and date not in (select date from hr_holidays_public_line where date >= %s and date <= %s)
            and date not in (select generate_series(hh.date_from::date, hh.date_to::date, '1 day')::date as date from hr_holidays hh,hr_holidays_status ss  where hh.holiday_status_id = ss.id and hh.type='remove' and hh.employee_id =%s and hh.date_to >= %s and hh.date_to <= hh.date_to)
            and absent =true and employee_id=%s""",(date_from, termination_date,date_from, termination_date,date_from, termination_date,employee_id,date_from,employee_id,))
            absent_data =cr.fetchone()
            if absent_data:
                absent_count=absent_data[0]
        elif initial_employment_date >= date_from and termination_date <= date_to:
            cr.execute("""select COALESCE( sum(normal),0) as normal  from attendance_data_import where 
            date >= %s and date <= %s and date not in (SELECT the_day ::date FROM  generate_series(%s::date, %s  ::date, '1 day') d(the_day) 
            WHERE  extract('ISODOW' FROM the_day)= 7)
            and date not in (select date from hr_holidays_public_line where date >= %s and date <= %s)
            and date not in (select generate_series(hh.date_from::date, hh.date_to::date, '1 day')::date as date from hr_holidays hh,hr_holidays_status ss  where hh.holiday_status_id = ss.id and hh.type='remove' and hh.employee_id =%s and hh.date_to >= %s and hh.date_to <= hh.date_to)
            and absent =true and employee_id=%s""",(initial_employment_date, termination_date,initial_employment_date, termination_date,initial_employment_date, termination_date,employee_id,initial_employment_date,employee_id,))
            absent_data =cr.fetchone()
            if absent_data:
                absent_count=absent_data[0]
        else:
            cr.execute("""select COALESCE( sum(normal),0) as normal  from attendance_data_import where 
            date >= %s and date <= %s and date not in (SELECT the_day ::date FROM  generate_series(%s::date, %s  ::date, '1 day') d(the_day) 
            WHERE  extract('ISODOW' FROM the_day)= 7)
            and date not in (select date from hr_holidays_public_line where date >= %s and date <= %s)
            and date not in (select generate_series(hh.date_from::date, hh.date_to::date, '1 day')::date as date from hr_holidays hh,hr_holidays_status ss  where hh.holiday_status_id = ss.id and hh.type='remove' and hh.employee_id =%s and hh.date_to >= %s and hh.date_to <= hh.date_to)
            and absent =true and employee_id=%s""",(date_from, date_to,date_from, date_to,date_from, date_to,employee_id,date_from,employee_id,))
            absent_data =cr.fetchone()
            if absent_data:
                absent_count=absent_data[0]
        cr.execute("""select COALESCE( sum(normal) ,0) as total_working_day  from attendance_data_import where 
        date between %s and  %s and date not in (SELECT the_day ::date FROM  generate_series(%s::date, %s  ::date, '1 day') d(the_day) 
        WHERE  extract('ISODOW' FROM the_day) = 7 )
        and date not in ( select hpl.date from hr_holidays_public_line hpl inner join hr_holidays_public hp on hpl.holidays_id = hp.id 
        where hpl.date between %s::date and %s::date)
        and date not in (select generate_series(date_from::date, date_to::date, '1 day')::date as date from hr_holidays where  employee_id =%s and date_to between  %s and %s )
        and absent != true and employee_id=%s""",(date_from, date_to,date_from, date_to,date_from, date_to,employee_id,date_from, date_to,employee_id,))
        present_data =cr.fetchone()
        cr.execute("select  COALESCE( sum(number_of_days_temp - floor(number_of_days_temp)))  as leave_count from hr_holidays  where  employee_id =%s and date_to between %s and %s ",(employee_id,date_from, date_to,))
        leave_half_count =cr.fetchone()[0]
        if leave_half_count is None:
            leave_half_count=0
        cr.execute("""select COALESCE( sum(normal),0) from attendance_data_import where
             --timetable in (select id from shift_timetable where shift_name='Afternoon') and 
             absent =true
            and extract('ISODOW' FROM date)= 6 and employee_id=%s and date between %s and %s""",(employee_id,date_from, date_to,))        
        sat_data =cr.fetchone()[0]
        if present_data:
            present_count=present_data[0]+leave_half_count
        else:
            present_count=0
        con_date  = date_from
        before_day=0
        after_day=0
        if initial_date > date_from:
            con_date =initial_date
            cr.execute("SELECT TRUNC(DATE_PART('day',  %s::timestamp - %s::timestamp))",(initial_date,date_from,))
            before_day=cr.fetchone()[0]
        if con_state == 'pending_done' and effective_date > date_from and termination_date < date_to:
            cr.execute( """select sum(count) as public_count from 
                (SELECT count(the_day ::date) FROM  generate_series(%s::date, %s::date, '1 day') d(the_day) 
                WHERE  extract('ISODOW' FROM the_day)= 7 and the_day ::date not in 
                (select generate_series(date_from::date, date_to::date, '1 day')::date as date from hr_holidays 
                where  employee_id =%s and date_from >=  date_from and date_to <= date_to) union all  
                select count(date) from hr_holidays_public_line where date between %s and %s and
                date not in (select generate_series(date_from::date, date_to::date, '1 day')::date as date from hr_holidays
                where employee_id =%s and date_from >=  date_from and date_to <= date_to))A""",(effective_date, termination_date,employee_id,effective_date,termination_date,employee_id ))   
            holiday_data =cr.fetchone()
            cr.execute("SELECT TRUNC(DATE_PART('day',  %s::timestamp - %s::timestamp))",(date_to,termination_date,))
            after_day=cr.fetchone()[0] 
        elif con_state == 'pending_done' and termination_date < date_to:
            cr.execute("""select sum(count) as public_count from 
                (SELECT count(the_day ::date) FROM  generate_series(%s::date, %s::date, '1 day') d(the_day) 
                WHERE  extract('ISODOW' FROM the_day)= 7 and the_day ::date not in 
                (select generate_series(date_from::date, date_to::date, '1 day')::date as date from hr_holidays 
                where  employee_id =%s and date_from >=  date_from and date_to <= date_to) union all  
                select count(date) from hr_holidays_public_line where date between %s and %s and
                date not in (select generate_series(date_from::date, date_to::date, '1 day')::date as date from hr_holidays
                where employee_id =%s and date_from >=  date_from and date_to <= date_to))A""",(date_from, termination_date,employee_id,date_from,termination_date,employee_id))   
            holiday_data =cr.fetchone()
            cr.execute("SELECT TRUNC(DATE_PART('day',  %s::timestamp - %s::timestamp))",(date_to,termination_date,))
            after_day=cr.fetchone()[0]
        elif con_state != 'pending_done' and effective_date > date_from:
            cr.execute( """select sum(count) as public_count from 
                (SELECT count(the_day ::date) FROM  generate_series(%s::date, %s::date, '1 day') d(the_day) 
                WHERE  extract('ISODOW' FROM the_day)= 7 and the_day ::date not in 
                (select generate_series(date_from::date, date_to::date, '1 day')::date as date from hr_holidays 
                where  employee_id =%s and date_from >=  date_from and date_to <= date_to) union all  
                select count(date) from hr_holidays_public_line where date between %s and %s and
                date not in (select generate_series(date_from::date, date_to::date, '1 day')::date as date from hr_holidays
                where employee_id =%s and date_from >=  date_from and date_to <= date_to))A""",(effective_date, date_to,employee_id,effective_date,date_to,employee_id ))   
            holiday_data =cr.fetchone()
        else:
            cr.execute( """select sum(count) as public_count from 
                (SELECT count(the_day ::date) FROM  generate_series(%s::date, %s::date, '1 day') d(the_day) 
                WHERE  extract('ISODOW' FROM the_day)= 7 and the_day ::date not in 
                (select generate_series(date_from::date, date_to::date, '1 day')::date as date from hr_holidays 
                where  employee_id =%s and date_from >=  date_from and date_to <= date_to) union all  
                select count(date) from hr_holidays_public_line where date between %s and %s and
                date not in (select generate_series(date_from::date, date_to::date, '1 day')::date as date from hr_holidays
                where employee_id =%s and date_from >=  date_from and date_to <= date_to))A""",(con_date, date_to,employee_id,con_date,date_to,employee_id ))   
            holiday_data =cr.fetchone()
        if holiday_data is not 0 or holiday_data is not False:
            holiday_count=holiday_data[0]  
        else:
            holiday_count=0        
        cr.execute(" select COALESCE( sum(duration),0) from hr_temporary_out where employee_id= %s and date between %s and %s",(employee_id,date_from, date_to,))      
        temporary_min =cr.fetchone()[0]
        cr.execute(" select COALESCE(sum(amount),0) from hr_efficiency_value where employee_id= %s and code ='EBS' and date between %s and %s",(employee_id,date_from, date_to,))      
        efficiency_value =cr.fetchone()[0]        
        cr.execute(" select COALESCE(sum(amount),0) from hr_efficiency_value where employee_id= %s and code ='QLB' and date between %s and %s",(employee_id,date_from, date_to,))      
        quality_value =cr.fetchone()[0]       
        cr.execute(" select COALESCE(sum(amount),0) from hr_efficiency_value where employee_id= %s and code ='PFB' and date between %s and %s",(employee_id,date_from, date_to,))      
        performance_bonus =cr.fetchone()[0]               
        cr.execute(" select COALESCE(sum(mark),0) from hr_performance_mark where employee_id= %s and code ='MARK' and date between %s and %s",(employee_id,date_from, date_to,))      
        performance_marking=cr.fetchone()[0]                                
        for contract in contract_obj.browse(cr, uid, contract_ids, context=context):
            for rule in rule_obj.browse(cr, uid, sorted_rule_ids, context=context):
                if rule.input_ids:
                    for input in rule.input_ids:
                        if input.code == 'ETI':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':total_income,
                               'contract_id': contract.id,
                              }
                        else:
                            inputs = {
                                     'name': input.name,
                                     'code': input.code,
                                     'amount':0.0,
                                     'contract_id': contract.id,
                                }
                        if input.code == 'PET':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':tax_paid,
                               'contract_id': contract.id,
                              }
                        if input.code == 'PPT':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':income_tax,
                               'contract_id': contract.id,
                              } 
                        if input.code == 'PTI':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':payroll_total_income,
                               'contract_id': contract.id,
                              }                         
                        if input.code == 'DPD':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':deposit_amount,
                               'contract_id': contract.id,
                              }
                        if input.code == 'UCL':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':claim_amount,
                               'contract_id': contract.id,
                              }
                        if input.code == 'LON':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':loan_amount,
                               'contract_id': contract.id,
                              }
                        if input.code == 'FINE':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':fine_amount,
                               'contract_id': contract.id,
                              }
                        if input.code == 'SSB':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':ssb_amount,
                               'contract_id': contract.id,
                              }
                        if input.code == 'SB':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':service_bonus,
                               'contract_id': contract.id,
                              }
                        if input.code == 'TLC':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':trip_amount,
                               'contract_id': contract.id,
                              }                         
                        if input.code == 'OM':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':ot_minus,
                               'contract_id': contract.id,
                              } 
                        if input.code == 'SPOM':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':sun_holiday_ot_min,
                               'contract_id': contract.id,
                              }
                        if input.code == 'OTD':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':ot_day_count,
                               'contract_id': contract.id,
                              } 
                        if input.code == 'SPDT':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':sun_holiday_ot_day,
                               'contract_id': contract.id,
                              }              
                        if input.code == 'EM':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':early_minus,
                               'contract_id': contract.id,
                              }                
                        if input.code == 'LM':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':late_min,
                               'contract_id': contract.id,
                              }
                        if input.code == 'LC':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':late_count,
                               'contract_id': contract.id,
                              }
                        if input.code == 'EC':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':early_count,
                               'contract_id': contract.id,
                              }
                        if input.code == 'MPC':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':misspunch_count,
                               'contract_id': contract.id,
                              }                  
                        if input.code == 'AC':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':absent_count,
                               'contract_id': contract.id,
                              }        
                        if input.code == 'PC':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':present_count,
                               'contract_id': contract.id,
                              }  
                        if input.code == 'AWH':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':actual_working_hour,
                               'contract_id': contract.id,
                              }              
                        if input.code == 'HC':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':holiday_count,
                               'contract_id': contract.id,
                              }         
                        if input.code == 'GPTO':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':temporary_min,
                               'contract_id': contract.id,
                              }                     
                        if input.code == 'BDC':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':before_day,
                               'contract_id': contract.id,
                              }
                        if input.code == 'ADC':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':after_day,
                               'contract_id': contract.id,
                              }    
                        if input.code == 'EBS':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':efficiency_value,
                               'contract_id': contract.id,
                              }                
                        if input.code == 'QLB':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':quality_value,
                               'contract_id': contract.id,
                              }                                        
                        if input.code == 'PFB':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':performance_bonus,
                               'contract_id': contract.id,
                              }      
                        if input.code == 'MARK':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':performance_marking,
                               'contract_id': contract.id,
                              }                                                                                                                                                                                                                                                                                                                            
                        res += [inputs]
        return res
    
    def get_worked_day_lines(self, cr, uid, contract_ids, date_from, date_to, context=None):
        """
        @param contract_ids: list of contract id
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        second_type=False
        day_from = datetime.strptime(date_from, "%Y-%m-%d").date()
        day_to = datetime.strptime(date_to, "%Y-%m-%d").date()
        month_days = calendar.monthrange(day_from.year, day_from.month)[1]   
        cr.execute('select employee_id,date_start from hr_contract where id = %s', (contract_ids))
        employee_data = cr.fetchone() 
        if  employee_data:
            employee_id=employee_data[0]
            initial_date=employee_data[1]
        cr.execute('select initial_employment_date,birthday from hr_employee where id = %s', (employee_id,))
        employee_datas = cr.fetchone()
        if employee_datas:
            joining_date =employee_datas[0]     
            birthday = employee_datas[1]
        age_for_ssb =0
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        if birthday:
            birth_date = parser.parse(birthday)
            age_for_ssb = current_year - birth_date.year  
        working_month = 0
        cr.execute("SELECT EXTRACT(MONTH FROM %s::date) as next_month", (date_from,))
        next_month = cr.fetchone()[0]
        
        if int(next_month) is 1 or int(next_month) is 2 or int(next_month) is 3:
            cr.execute("SELECT EXTRACT(YEAR FROM %s::date) as next_year", (date_from,))
            next_year = cr.fetchone()        
        else:
            cr.execute("SELECT EXTRACT(YEAR FROM %s::date)+1 as next_year", (date_from,))
            next_year = cr.fetchone()
        if next_year[0] is not None: 
            next_year = int(next_year[0])       
              
            cr.execute("SELECT (date_part('year',age('%s-03-01', %s)) * 12 )+date_part('month',age('%s-04-01', %s)) as w_month", (next_year, date_to, next_year, date_to,))
            w_month = cr.fetchone()
            if w_month:
                if w_month[0] >= 12:
                    working_month = 12;
                else:
                    working_month = w_month[0]     
        #cr.execute("SELECT (date_part('month',age('%s-04-01',%s))) + 1 as month ",(next_year,joining_date,))
        cr.execute("SELECT (DATE_PART('year', '%s-04-01'::date) - DATE_PART('year', %s::date)) * 12 + (DATE_PART('month', '%s-04-01'::date) - DATE_PART('month', %s::date)) as month ",(next_year,joining_date,next_year,joining_date,))
        total_working_month =cr.fetchone()[0]
        if total_working_month >12:
            total_working_month=12  
##########################BW-243:Change FAIR DEAL Version(19-09-2018)#########################################################			
        def was_on_leave(employee_id, datetime_day, context=None):
            # res = False
            leave_type = False
            day_temp = False
            second_type=False
            second_day_temp=False
            day = datetime_day.strftime("%Y-%m-%d")
            holiday_ids = self.pool.get('hr.holidays').search(cr, uid, [('state', '=', 'validate'), ('employee_id', '=', employee_id), ('type', '=', 'remove'), ('date_from', '<=', day), ('date_to', '>=', day)])
            if holiday_ids:
                if len(holiday_ids)>1:
                    leave_type = self.pool.get('hr.holidays').browse(cr, uid, holiday_ids, context=context)[0].holiday_status_id.name
                    day_temp = self.pool.get('hr.holidays').browse(cr, uid, holiday_ids, context=context)[0].number_of_days_temp            
                    second_type = self.pool.get('hr.holidays').browse(cr, uid, holiday_ids, context=context)[1].holiday_status_id.name
                    second_day_temp = self.pool.get('hr.holidays').browse(cr, uid, holiday_ids, context=context)[1].number_of_days_temp
                else:   
                    leave_type = self.pool.get('hr.holidays').browse(cr, uid, holiday_ids, context=context)[0].holiday_status_id.name
                    day_temp = self.pool.get('hr.holidays').browse(cr, uid, holiday_ids, context=context)[0].number_of_days_temp                    
            return leave_type, day_temp ,second_type ,second_day_temp

        res = []
        for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context):
            if not contract.working_hours:
                # fill only if the contract as a working schedule linked
                continue
            # add function return from store procedure  
            effective_day = datetime.strptime(contract.effective_date, "%Y-%m-%d") 
            last_working_day = datetime.strptime(contract.date_end, "%Y-%m-%d")
            effective_date = datetime.strptime(contract.effective_date, "%Y-%m-%d").date()    
            last_working_date = datetime.strptime(contract.date_end, "%Y-%m-%d").date()                            
            day_from = datetime.strptime(date_from, "%Y-%m-%d")
            day_to = datetime.strptime(date_to, "%Y-%m-%d")
            date_start = datetime.strptime(date_from, "%Y-%m-%d").date()
            date_end = datetime.strptime(date_to, "%Y-%m-%d").date()
            period_end =day_to+ timedelta(days=1)
            if effective_date >= date_start and last_working_date >= date_end:
                nb_of_days = (day_to - effective_day).days + 1
            elif effective_date <= date_start and last_working_date <= date_end:
                nb_of_days = (last_working_day - day_from).days + 1
            elif effective_date >= date_start and last_working_date <= date_end:
                nb_of_days = (last_working_day - effective_day).days + 1
            else:
                nb_of_days = (day_to - day_from).days + 1
            total_nb_of_days = (day_to - day_from).days + 1
            attendances = {
                 'name': _("Normal Working Days paid at 100%"),
                 'sequence': 0,
                 'code': 'WORK100',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'number_of_minutes':0.0,
                'total_month_day':nb_of_days,
                'total_no_of_days':total_nb_of_days,
                'working_month':working_month,
                'real_working_month':total_working_month,
                'age_for_ssb':age_for_ssb,
                 'contract_id': contract.id,
            }
            leaves = {}
            day_from = datetime.strptime(date_from, "%Y-%m-%d")
            day_to = datetime.strptime(date_to, "%Y-%m-%d")
            if effective_date > date_start and last_working_date >= date_end:
                for day in range(0, nb_of_days):
                    working_hours_on_day = self.pool.get('resource.calendar').working_hours_on_day(cr, uid, contract.working_hours, effective_day + timedelta(days=day), context)
                    cr.execute('select sum(number_of_days)*-1 as leave from hr_holidays where number_of_days<0 and employee_id=%s and date_from between %s and %s', (contract.employee_id.id, day_from, day_to))   
                    leave = cr.fetchone()
                    if leave:
                        leave_day = leave[0]
                        if leave_day is None:
                            leave_day = 0.0
                    else:
                        leave_day = 0.0
                    if working_hours_on_day:
                        # the employee had to work
                        leave_type, day_temp ,second_type ,second_day_temp= was_on_leave(contract.employee_id.id, effective_day + timedelta(days=day), context=context)
                        if leave_type:
                            # if he was on leave, fill the leaves dict
                            if leave_type in leaves and day_temp != 0.5:
                                leaves[leave_type]['number_of_days'] += 1
                                leaves[leave_type]['number_of_hours'] += working_hours_on_day
                            elif leave_type in leaves  and day_temp == 0.5 :
    
                                leaves[leave_type]['number_of_days'] += day_temp
                                leaves[leave_type]['number_of_hours'] += working_hours_on_day / 2   
                                 
                            elif day_temp == 0.5:
    
                                leaves[leave_type] = {
                                    'name': leave_type,
                                    'sequence': 5,
                                    'code': leave_type,
                                    'number_of_days': day_temp,
                                    'number_of_hours': working_hours_on_day / 2,
                                    'contract_id': contract.id,
                                }
                            elif day_temp != 0.5:
                                leaves[leave_type] = {
                                    'name': leave_type,
                                    'sequence': 5,
                                    'code': leave_type,
                                    'number_of_days': 1.0,
                                    'number_of_hours': working_hours_on_day,
                                    'contract_id': contract.id,
                                }
                        if second_type:

                            if second_type in leaves  and second_day_temp == 0.5 :
    
                                leaves[second_type]['number_of_days'] += second_day_temp
                                leaves[second_type]['number_of_hours'] += working_hours_on_day / 2   
                                 
                            elif second_day_temp == 0.5:
    
                                leaves[second_type] = {
                                    'name': second_type,
                                    'sequence': 5,
                                    'code': second_type,
                                    'number_of_days': second_day_temp,
                                    'number_of_hours': working_hours_on_day / 2,
                                    'contract_id': contract.id,
                                }                                           
                        else:
                            attendances['number_of_days'] += 1.0
                            attendances['number_of_hours'] += working_hours_on_day
            elif effective_date > date_start and last_working_date < date_end:   
                for day in range(0, nb_of_days):
                    working_hours_on_day = self.pool.get('resource.calendar').working_hours_on_day(cr, uid, contract.working_hours, effective_day + timedelta(days=day), context)
                    cr.execute('select sum(number_of_days)*-1 as leave from hr_holidays where number_of_days<0 and employee_id=%s and date_from between %s and %s', (contract.employee_id.id, day_from, day_to))   
                    leave = cr.fetchone()
                    if leave:
                        leave_day = leave[0]
                        if leave_day is None:
                            leave_day = 0.0
                    else:
                        leave_day = 0.0
                    if working_hours_on_day:
                        # the employee had to work
                        leave_type, day_temp,second_type ,second_day_temp = was_on_leave(contract.employee_id.id, effective_day + timedelta(days=day), context=context)
                        if leave_type:
                            # if he was on leave, fill the leaves dict
                            if leave_type in leaves and day_temp != 0.5:
                                leaves[leave_type]['number_of_days'] += 1
                                leaves[leave_type]['number_of_hours'] += working_hours_on_day
                            elif leave_type in leaves  and day_temp == 0.5 :
    
                                leaves[leave_type]['number_of_days'] += day_temp
                                leaves[leave_type]['number_of_hours'] += working_hours_on_day / 2   
                                 
                            elif day_temp == 0.5:
    
                                leaves[leave_type] = {
                                    'name': leave_type,
                                    'sequence': 5,
                                    'code': leave_type,
                                    'number_of_days': day_temp,
                                    'number_of_hours': working_hours_on_day / 2,
                                    'contract_id': contract.id,
                                }
                            elif day_temp != 0.5:
                                leaves[leave_type] = {
                                    'name': leave_type,
                                    'sequence': 5,
                                    'code': leave_type,
                                    'number_of_days': 1.0,
                                    'number_of_hours': working_hours_on_day,
                                    'contract_id': contract.id,
                                }
                        if second_type:

                            if second_type in leaves  and second_day_temp == 0.5 :
    
                                leaves[second_type]['number_of_days'] += second_day_temp
                                leaves[second_type]['number_of_hours'] += working_hours_on_day / 2   
                                 
                            elif second_day_temp == 0.5:
    
                                leaves[second_type] = {
                                    'name': second_type,
                                    'sequence': 5,
                                    'code': second_type,
                                    'number_of_days': second_day_temp,
                                    'number_of_hours': working_hours_on_day / 2,
                                    'contract_id': contract.id,
                                }                                              
                        else:
                            attendances['number_of_days'] += 1.0
                            attendances['number_of_hours'] += working_hours_on_day
            else:
                for day in range(0, nb_of_days):
                    working_hours_on_day = self.pool.get('resource.calendar').working_hours_on_day(cr, uid, contract.working_hours, day_from + timedelta(days=day), context)
                    cr.execute('select sum(number_of_days)*-1 as leave from hr_holidays where number_of_days<0 and employee_id=%s and date_from between %s and %s', (contract.employee_id.id, day_from, day_to))   
                    leave = cr.fetchone()
                    if leave:
                        leave_day = leave[0]
                        if leave_day is None:
                            leave_day = 0.0
                    else:
                        leave_day = 0.0
                    if working_hours_on_day:
                        # the employee had to work
                        leave_type, day_temp,second_type ,second_day_temp = was_on_leave(contract.employee_id.id, day_from + timedelta(days=day), context=context)
                        if leave_type:
                            # if he was on leave, fill the leaves dict
                            if leave_type in leaves and day_temp != 0.5:
                                leaves[leave_type]['number_of_days'] += 1
                                leaves[leave_type]['number_of_hours'] += working_hours_on_day
                            elif leave_type in leaves  and day_temp == 0.5 :
    
                                leaves[leave_type]['number_of_days'] += day_temp
                                leaves[leave_type]['number_of_hours'] += working_hours_on_day / 2   
                                 
                            elif day_temp == 0.5:
    
                                leaves[leave_type] = {
                                    'name': leave_type,
                                    'sequence': 5,
                                    'code': leave_type,
                                    'number_of_days': day_temp,
                                    'number_of_hours': working_hours_on_day / 2,
                                    'contract_id': contract.id,
                                }
                            elif day_temp != 0.5:
                                leaves[leave_type] = {
                                    'name': leave_type,
                                    'sequence': 5,
                                    'code': leave_type,
                                    'number_of_days': 1.0,
                                    'number_of_hours': working_hours_on_day,
                                    'contract_id': contract.id,
                                }
                        if second_type:
    
                            if second_type in leaves  and second_day_temp == 0.5 :
    
                                leaves[second_type]['number_of_days'] += second_day_temp
                                leaves[second_type]['number_of_hours'] += working_hours_on_day / 2   
                                 
                            elif second_day_temp == 0.5:
    
                                leaves[second_type] = {
                                    'name': second_type,
                                    'sequence': 5,
                                    'code': second_type,
                                    'number_of_days': second_day_temp,
                                    'number_of_hours': working_hours_on_day / 2,
                                    'contract_id': contract.id,
                                }                                                  
                            else:
                                attendances['number_of_days'] += 1.0
                                attendances['number_of_hours'] += working_hours_on_day               
            leaves = [value for key, value in leaves.items()]
            if effective_date > date_start and last_working_date > date_end:
                cr.execute("select count(id) from hr_holidays_public_line where date between %s and  %s ",(effective_date,day_to,))
                public_count =cr.fetchone()
                if public_count:
                    public_count=public_count[0]
                else:
                    public_count=0
            elif effective_date < date_start and last_working_date < date_end:
                cr.execute("select count(id) from hr_holidays_public_line where date between %s and  %s ",(date_from,last_working_date,))
                public_count =cr.fetchone()
                if public_count:
                    public_count=public_count[0]
                else:
                    public_count=0
            elif effective_date > date_start and last_working_date < date_end:
                cr.execute("select count(id) from hr_holidays_public_line where date between %s and  %s ",(effective_date,last_working_date,))
                public_count =cr.fetchone()
                if public_count:
                    public_count=public_count[0]
                else:
                    public_count=0
            else:
                cr.execute("select count(id) from hr_holidays_public_line where date between %s and  %s ",(date_from,date_to,))
                public_count =cr.fetchone()
                if public_count:
                    public_count=public_count[0]
                else:
                    public_count=0
            before_day=0
            sun_count=0
            if initial_date > date_from:
                cr.execute("SELECT TRUNC(DATE_PART('day',  %s::timestamp - %s::timestamp))",(initial_date,date_from,))
                before_day=cr.fetchone()[0]
            if effective_date > date_start and last_working_date >= date_end:
                cr.execute("SELECT count(the_day ::date) as sun_count FROM generate_series(%s::date, %s ::date, '1 day') d(the_day)  WHERE  extract('ISODOW' FROM the_day) = 7  ",(str(effective_date),date_to,))
                sun_count =cr.fetchone()[0]
            elif effective_date < date_start and last_working_date < date_end:   
                cr.execute("SELECT count(the_day ::date) as sun_count FROM generate_series(%s::date, %s ::date, '1 day') d(the_day)  WHERE  extract('ISODOW' FROM the_day) = 7  ",(date_from,str(last_working_day),))
                sun_count =cr.fetchone()[0]     
            elif effective_date > date_start and last_working_date < date_end:
                cr.execute("SELECT count(the_day ::date) as sun_count FROM generate_series(%s::date, %s ::date, '1 day') d(the_day)  WHERE  extract('ISODOW' FROM the_day) = 7  ",(effective_day,last_working_day,))
                sun_count =cr.fetchone()[0]    
            else:
                cr.execute("SELECT count(the_day ::date) as sun_count FROM generate_series(%s::date, %s ::date, '1 day') d(the_day)  WHERE  extract('ISODOW' FROM the_day) = 7  ",(date_from,date_to,))
                sun_count =cr.fetchone()[0]
            cr.execute("SELECT count(the_day ::date) as sat_count FROM generate_series(%s::date, %s ::date, '1 day') d(the_day)  WHERE  extract('ISODOW' FROM the_day) = 6  ",(day_from,day_to,))
            sat_count =cr.fetchone()
            if sat_count:
                sat_count=sat_count[0]/2
            else:
                sat_count=0  
######################## END BW-243:Change FAIR DEAL Version(19-09-2018)###########################################################						
            cr.execute("select  COALESCE( sum(number_of_days_temp - floor(number_of_days_temp)))  as leave_count from hr_holidays  where  employee_id =%s and date_to between %s and %s ",(contract.employee_id.id,date_from, date_to,))
            leave_half_count =cr.fetchone()[0]
            if leave_half_count is None:
                leave_half_count=0
            cr.execute("select  COALESCE( sum(number_of_days_temp))  as leave_count from hr_holidays  where  employee_id =%s and date_to between %s and %s ",(contract.employee_id.id,date_from, period_end,))
            leave_count =cr.fetchone()[0]
            if leave_count is None:
                leave_count=0 
            sun_leave=0
            if leaves:
                for leave in leaves:
                    cr.execute("""SELECT count(the_day::date) as date FROM generate_series(%s::date, %s ::date, '1 day') d(the_day)  
                    WHERE  extract('ISODOW' FROM the_day) = 7 and the_day::date in
                    (select generate_series(hh.date_from::date, hh.date_to::date, '1 day')::date as date from hr_holidays hh,hr_holidays_status hhs
                    WHERE hh.holiday_status_id=hhs.id and hh.type='remove' and employee_id=%s and date_from >=  date_from and date_to <= date_to
                    and hhs.name=%s)""",(date_from,date_to, employee_id,leave['code'],))
                    sun_leave =cr.fetchone()[0] 
                    if sun_leave>0:
                        cr.execute("""select hhs.name from hr_holidays hh,hr_holidays_status hhs
                        WHERE hh.holiday_status_id=hhs.id and hh.type='remove' and employee_id=%s and date_from >=  date_from and date_to <= date_to
                        and hhs.name=%s""",(employee_id,leave['code']))
                        leave_name = cr.fetchone()[0]
                        if leave_name == leave['code']:
                            leave['number_of_days'] += sun_leave           
            attendances['number_of_days'] = (nb_of_days - (public_count + sun_count + leave_count))
            res += [attendances] + leaves 
        return res
