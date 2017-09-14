from openerp.osv import orm
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime


class attendance_data_import(osv.osv):

    _name = "attendance.data.import"    
    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Name'),
        'fingerprint_id': fields.char('Emp No'),
        'auto_assign': fields.char('Auto Assign'),
        'date': fields.date('Date'),
        'timetable': fields.char('Timetable'),
        'onduty': fields.char('On duty'),
        'offduty': fields.char('Off duty'),
        'clockin': fields.char('Clock In'),
        'clockout': fields.char('Clock Out'),
        'normal': fields.float('Normal'),
        'realtime': fields.float('Realtime'),
        'late': fields.integer('Late'),
        'early': fields.integer('Early'),
        'absent': fields.boolean('Absent'),
        'ot_time': fields.integer('OT Time'),
        'work_time': fields.integer('Work Time'),
        'exception': fields.integer('Exception'),
        'must_in': fields.boolean('MustC In'),
        'must_out': fields.boolean('MustC Out'),
        'department_id': fields.many2one('hr.department', 'Department'),
        'ndays': fields.float('NDays'),
        'weekend': fields.float('WeekEnd'),
        'holiday': fields.float('Holiday'),
        'att_time': fields.integer('Att Time'),
        'ndays_ot': fields.integer('NDays OT'),
        'weekend_ot': fields.float('Weekend OT'),
        'holiday_ot': fields.float('Holiday OT'),
        'state':fields.selection([
                ('draft', 'Draft'),
                ('approve', 'Approved'),
                ('decline', 'Decline'),
                ], 'Status',default='draft'),
        'remark': fields.text('Remark'),
    }
#     def calculate_on_change(self,cr,uid, ids,on_duty,off_duty,clock_in, clock_out, context=None):
#         result = {}
#         start_time = end_time = None
#         late = early = late_t = early_t = 0
#         FMT = '%H:%M'
#         if clock_in and on_duty:
#             late_t = datetime.strptime(on_duty, FMT) - datetime.strptime(clock_in, FMT)
#         if clock_out and off_duty:
#            early_t = datetime.strptime(off_duty, FMT) - datetime.strptime(clock_out, FMT)     
#         
#         if int(late_t) < 0:
#             late_t = late_t * -1        
#         if int(early_t) < 0:
#             early_t = early_t * -1
#         result = {'late': late_t,                       
#                   'early': early_t,                      
#                  } 
#                        
#         return {'value':result}
    def calculate_on_change(self,cr,uid, ids,on_duty,off_duty,clock_in, clock_out, context=None):
        result = {}
        start_time = end_time =  None
        late = early = late_t = early_t = realtime =  0
        FMT = '%H:%M'
        absent = False
        try:
            if clock_in and on_duty:
                on_duty = "2014-04-25 " + on_duty + ":00"
                clock_in = "2014-04-25 " + clock_in + ":00" 
                cr.execute("""select extract (epoch from (timestamp %s - timestamp %s))::integer/60""",(on_duty,clock_in,))
                late_date = cr.fetchall()
                if late_date:
                    late = late_date[0][0]
            if clock_out and off_duty:
                off_duty = "2014-04-25 " + off_duty + ":00"
                clock_out = "2014-04-25 " + clock_out + ":00" 
                cr.execute("""select extract (epoch from (timestamp %s - timestamp %s))::integer/60""",(clock_out,off_duty,))             
                early_date = cr.fetchall()
                if early_date:
                    early = early_date[0][0]    
            
            if int(late) < 0:
                late_t = late * -1
                #late_t = self.convert_hour_minute(int(late))
            if int(early) < 0:
                early_t = early * -1   
                #early_t = self.convert_hour_minute(int(early))
            
            if clock_in or clock_out:
               absent = False
               realtime = 0.5
            else:
               absent = True
               realtime = 0.0    
            result = {'late': str(late_t),                       
                      'early': str(early_t),
                      'absent': absent,
                      'realtime': realtime,                      
                     } 
                           
            return {'value':result}
        except Exception, e:            
            raise orm.except_orm(_('Error :'), _("Error while processing input time. \n\nPlease check time format must be HH:MM!"))
    def convert_hour_minute(self,t_time):
        total = None
        
        if t_time < 0:
            t_time = t_time * -1
            
        modulus = remainder = 0
        modulus = t_time / 60
        remainder = t_time % 60
        if modulus == 0:
            total = "00:"
        else:
            total = str(modulus)
        if remainder == 0:
           total += "00"
        else:
           total += str(remainder)
        return total      
    def decline(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'decline'}, context=context)
        return True
    def approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'approve'}, context=context)
        return True
    def set_to_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'}, context=context)
        return True   
attendance_data_import()   



    