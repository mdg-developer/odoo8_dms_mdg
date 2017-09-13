from openerp.osv import fields, osv
from openerp.tools.translate import _
import time
import datetime 
from datetime import datetime,date, timedelta
import calendar

class hr_leave_type(osv.osv):

    _name = 'hr.leave.type'
    
    _columns = {
        'holiday_status_id': fields.many2one('hr.holidays.status','Leave Type', required=True),
        'name': fields.char('Leave Type Name'),
        'category_ids': fields.many2many('hr.employee.category', 'leave_employee_category_rel', 'leavetype_id', 'category_id', 'Employee Tags'),
        'categ_id': fields.many2one('calendar.event.type', 'Meeting Type'),
        'gender':fields.selection([
                ('male', 'Male'),
                ('female', 'Female'),
                ('both', 'Both'),
            ], 'Gender'),
        'validity': fields.integer('Validity'),
        'duration_before_allocation_type':fields.selection([
                ('day', 'Day(s)'),
                ('month', 'Month(s)'),
                ('year', 'Year(s)'),
            ], ''),
        'based_on':fields.selection([
                ('joined_date', 'Joined Date'),
                ('permanent', 'Permanent'),
                #('calendar_year', 'Calendar Year'),
                #('financial_year', 'Financial Year'),
            ], 'Based On'),
        'duration_before_allocation': fields.integer('Duration Before Allocation'),
        'max_days_tobe_allocated': fields.integer('Maximum Days To Be Allocated'),
        'min_days_per_month': fields.integer('Minimum Number of Days Worked Per Month'),
        'deduct_per_month': fields.boolean('Deduct Based On Number of Days per Month', help='If you select this check box, the system allows to calculate leave by leave type according to the attendance of emp last year.'),
        'allocate_frequency':fields.selection([
                ('yearly', 'Yearly'),
                ('monthly', 'Monthly'),
            ], 'Allocate Frequency'),
    }
    
    def calculate_no_of_att_days(self, cr, uid, context=None):
        days_data_pool = self.pool.get("hr.emp.workingdays.permonth")
        emp_ids = self.pool['hr.employee'].search(cr, uid,[('status', 'in', ['pending_inactive','active','onboarding','new','reactivated']),
                                                                ], context=context)
        
        start_date=datetime.today()
        start_date = start_date.replace(day=1)
        _, days_in_month = calendar.monthrange(start_date.year, start_date.month)
        end_date = start_date + timedelta(days=days_in_month-1)
        sd=start_date.strftime ("%Y-%m-%d")
        ed=end_date.strftime ("%Y-%m-%d")
        values = {} 
        if emp_ids:
            for e in emp_ids:                
                cr.execute("select COALESCE( sum(normal) ,0) as total_working_day,employee_id  from attendance_data_import where \
                date between %s and  %s and date not in (SELECT the_day ::date FROM  generate_series(%s::date, %s::date, '1 day') d(the_day) \
                WHERE  extract('ISODOW' FROM the_day) = 7 )\
                and date not in ( select date from hr_holidays_public_line where date between %s and  %s )\
                and date not in (select generate_series(date_from::date, date_to::date, '1 day')::date as date from hr_holidays where  employee_id= %s and date_to between  %s and %s )\
                and absent != true and employee_id= %s group by employee_id order by employee_id",(sd, ed,sd, ed,sd, ed,e,sd, ed,e))
                present_data =cr.fetchone()
                cr.execute("select COALESCE( sum(normal),0) as sat_working_day,employee_id from attendance_data_import where absent !=true  and extract('ISODOW' FROM date)= 6  and employee_id=%s and date between  %s  and  %s group by employee_id order by employee_id",(e,sd, ed,))        
                sat_data =cr.fetchone()
                if not sat_data:
                    sat_count=0
                else:
                    sat_count=sat_data[0]
                if present_data or sat_data:
                    values ={
                              'from_date': start_date,
                              'to_date':  end_date,
                              'no_of_days': present_data[0]+ (sat_count * 2) ,
                              'month': datetime.now().month,
                              'year': datetime.now().year,
                              'employee_id': e,
                          }                   
                    if values:
                        days_data_pool.create(cr, uid, values, context=context)
        
        print '?????? ' + 'calculate_no_of_att_days' + ' ??????';
        return True   
    
    def on_change_leavetype(self, cr, uid, ids, holiday_status_id, context=None):
        values = {}
        if holiday_status_id:
            leave = self.pool.get('hr.holidays.status').browse(cr, uid, holiday_status_id, context=context)
            values = {  
                'name': leave.name,               
            }
        return {'value': values} 
    
    def auto_allocate_leaves(self, cr, uid, context=None):
        leave_type_obj = self.pool.get("hr.holidays.status")        
        leave_type_ids=leave_type_obj.search(cr, uid, [('active','=','t')])
        print '?????? ' + 'auto_allocate_leaves' + ' ??????';
        for r in leave_type_ids:
            cr.callproc('auto_allocate_leave', (r,))
            res = cr.dictfetchall()
        return True      
    
hr_leave_type()