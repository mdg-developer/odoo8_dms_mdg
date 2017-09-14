from openerp.osv import fields, osv
from openerp.tools.translate import _
import time
import math
from datetime import datetime
from datetime import datetime,date, timedelta
import calendar
#import datetime

class hr_holidays(osv.osv):

    _name = 'hr.holidays'
    _inherit = ['hr.holidays']    
   
    emp_id=False;
    _columns = {
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscalyear'),        
        'effective_date': fields.date('Effective Date'),
        'expiry_date': fields.date('Expiry Date', required=True),
        'section_id':fields.related('employee_id', 'section_id', string='Section', type='many2one', relation='hr.section', readonly=True, store=True),
        'badge_id':fields.related('employee_id', 'employee_id', string='Badge ID', type='char', relation='hr.employee', readonly=True, store=True),       
    }
    def onchange_employee(self, cr, uid, ids, employee_id):
        result = {'value': {'department_id': False,'section_id':False,'badge_id':False}}
        global emp_id
        if employee_id:
            emp_id=employee_id
            employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            result['value'] = {'department_id': employee.department_id.id,'section_id':employee.section_id.id,'badge_id':employee.employee_id}
        return result
    
    def onchange_leave_type(self, cr, uid, ids, holiday_status_id):
        global emp_id
        result = {'value': {'holiday_status_id': False}}
        if holiday_status_id:
            now_date=datetime.now().strftime ("%Y-%m-%d")
            holiday_id = self.pool['hr.holidays'].search(cr, uid, [('employee_id', '=', emp_id),
                                                                ('type', '=', 'add'),
                                                                ('holiday_status_id', '=', holiday_status_id),
                                                                ('expiry_date', '>=', now_date)
                                                                ])
            dates = self.pool.get('hr.holidays').browse(cr, uid, holiday_id)
            result['value'] = {'effective_date': dates.effective_date ,'expiry_date': dates.expiry_date ,}
        return result
    
    def create(self, cr, uid, values, context=None):
        """ Override to avoid automatic logging of creation """
        if context is None:
            context = {}
        #now = datetime.datetime.now()
        acc_fy = self.pool.get('account.fiscalyear')
        fys = self.pool['account.fiscalyear'].search(cr, uid, [('date_stop','>=',time.strftime("%Y-%m-%d")),('date_start','<=',time.strftime("%Y-%m-%d")) ])
        for fid in fys:
            values.update({
                'fiscalyear_id': fid,
            }) 
        expiry_date = values.get('expiry_date', False)
        if expiry_date < datetime.now().strftime ("%Y-%m-%d"):
            raise osv.except_osv(_('Warning!'), _('Expiry Date must be greater than today.'))
        employee_id = values.get('employee_id', False)
        context = dict(context, mail_create_nolog=True, mail_create_nosubscribe=True)
        if values.get('state') and values['state'] not in ['draft', 'confirm', 'cancel'] and not self.pool['res.users'].has_group(cr, uid, 'base.group_hr_user'):
            raise osv.except_osv(_('Warning!'), _('You cannot set a leave request as \'%s\'. Contact a human resource manager.') % values.get('state'))
        currentMonth = datetime.now().month
        date_from = values.get('date_from', False)
        date_to = values.get('date_to', False)
        if date_from and date_to:
            from_date = datetime.strptime(date_from, "%Y-%m-%d %H:%M:%S").date()
            to_date = datetime.strptime(date_to, "%Y-%m-%d %H:%M:%S").date()
            if from_date.month == currentMonth and to_date.month == currentMonth:
                cr.execute("""select sum(number_of_days_temp) as number_of_days 
                            from hr_holidays hh,hr_holidays_status hhs
                            where hh.holiday_status_id=hhs.id
                            and type='remove' 
                            and employee_id=%s
                            and lower(hhs.name)='casual leave'""",(employee_id,))
                data = cr.fetchone()[0]
                if data is None:
                    data = 0.0
                result = {'value': {}}
                diff_day = self._get_number_of_days(date_from,date_to)
                result['value']['number_of_days_temp'] = round(math.floor(diff_day))+1
                day_count = data + result['value']['number_of_days_temp']
                leave_type_id = values.get('holiday_status_id', False)
                if leave_type_id:
                    cr.execute("""select name from hr_holidays_status  where id=%s """,(leave_type_id,))
                    leave_name = cr.fetchone()[0]
                if day_count:
                    if day_count > 3.00 and leave_name=='Casual Leave':
                        raise osv.except_osv(_('Warning!'),
                                             _('You cannot take more than 3 days'))
                #Casual Leave cannot join with other leave type#        
                y_date=from_date - timedelta(days=1)
                if y_date:
                    cr.execute("""select hh.*  from hr_holidays hh,hr_holidays_status hhs
                        where hh.holiday_status_id=hhs.id
                        and type='remove' 
                        and employee_id=%s
                        and date_to::date=%s
                        and lower(hhs.name)='casual leave'""",(employee_id,y_date,))
                    c_leave_filter_ids = cr.dictfetchall()  
                    cr.execute("""select hh.*  from hr_holidays hh,hr_holidays_status hhs
                        where hh.holiday_status_id=hhs.id
                        and type='remove' 
                        and employee_id=%s
                        and date_to::date=%s and lower(hhs.name) <> 'casual leave' """,(employee_id,y_date,))
                    leave_filter_ids = cr.dictfetchall()  
                 
                if ((leave_name <> 'Casual Leave' and leave_name<>'Unpaid') and c_leave_filter_ids) or (leave_name=='Casual Leave' and leave_filter_ids): 
                    raise osv.except_osv(_('Warning!'),
                                             _('Casual Leave can not join with other leave type.'))
                #Casual Leave cannot join with other leave type#       
        hr_holiday_id = super(hr_holidays, self).create(cr, uid, values, context=context)
        self.add_follower(cr, uid, [hr_holiday_id], employee_id, context=context)
        return hr_holiday_id
    
    def write(self, cr, uid, ids, vals, context=None):
        employee_id = vals.get('employee_id', False)
        expiry_date = vals.get('expiry_date', False)
#         if expiry_date < datetime.now().strftime ("%Y-%m-%d"):
#             raise osv.except_osv(_('Warning!'), _('Expiry Date must be greater than today.'))
        if vals.get('state') and vals['state'] not in ['draft', 'confirm', 'cancel'] and not self.pool['res.users'].has_group(cr, uid, 'base.group_hr_user'):
            raise osv.except_osv(_('Warning!'), _('You cannot set a leave request as \'%s\'. Contact a human resource manager.') % vals.get('state'))
        currentMonth = datetime.now().month
        date_from = vals.get('date_from', False)
        date_to = vals.get('date_to', False)
        if date_from and date_to:
            from_date = datetime.strptime(date_from, "%Y-%m-%d %H:%M:%S").date()
            to_date = datetime.strptime(date_to, "%Y-%m-%d %H:%M:%S").date()
            if employee_id is False:
                raise osv.except_osv(_('Warning!'),
                                                 _('Please Choose Again Employee Name'))
            if from_date.month == currentMonth and to_date.month == currentMonth:
                cr.execute("""select sum(number_of_days_temp) as number_of_days 
                            from hr_holidays hh,hr_holidays_status hhs
                            where hh.holiday_status_id=hhs.id
                            and type='remove' 
                            and employee_id=%s
                            and lower(hhs.name)='casual leave'""",(employee_id,))
                data = cr.fetchone()[0]
                if data is None:
                    data = 0.0
                result = {'value': {}}
                diff_day = self._get_number_of_days(date_from,date_to)
                result['value']['number_of_days_temp'] = round(math.floor(diff_day))+1
                day_count = data + result['value']['number_of_days_temp']
                leave_type_id = vals.get('holiday_status_id', False)
                if leave_type_id:
                    cr.execute("""select name from hr_holidays_status  where id=%s """,(leave_type_id,))
                    leave_name = cr.fetchone()[0]
                if day_count:
                    if day_count > 3.00 and leave_name=='Casual Leave':
                        raise osv.except_osv(_('Warning!'),
                                             _('You cannot take more than 3 days'))
                #Casual Leave cannot join with other leave type#        
                y_date=from_date - timedelta(days=1)
#                 leave_type_id = vals.get('holiday_status_id', False)
#                 if leave_type_id:
#                     cr.execute("""select name from hr_holidays_status  where id=%s """,(leave_type_id,))
#                     leave_name = cr.fetchone()[0]
                if y_date:
                    cr.execute("""select hh.*  from hr_holidays hh,hr_holidays_status hhs
                        where hh.holiday_status_id=hhs.id
                        and type='remove' 
                        and employee_id=%s
                        and date_to::date=%s
                        and lower(hhs.name)='casual leave'""",(employee_id,y_date,))
                    c_leave_filter_ids = cr.dictfetchall()  
                    cr.execute("""select hh.*  from hr_holidays hh,hr_holidays_status hhs
                        where hh.holiday_status_id=hhs.id
                        and type='remove' 
                        and employee_id=%s
                        and date_to::date=%s and lower(hhs.name) <> 'casual leave' """,(employee_id,y_date,))
                    leave_filter_ids = cr.dictfetchall()  
                 
                if ((leave_name <> 'Casual Leave' or leave_name<>'Unpaid') and c_leave_filter_ids) or (leave_name=='Casual Leave' and leave_filter_ids): 
                    raise osv.except_osv(_('Warning!'),
                                             _('Casual Leave can not join with other leave type.'))
                #Casual Leave cannot join with other leave type#       
        hr_holiday_id = super(hr_holidays, self).write(cr, uid, ids, vals, context=context)
        self.add_follower(cr, uid, ids, employee_id, context=context)
        return hr_holiday_id


hr_holidays()

class hr_holidays_status(osv.osv):

    _inherit = 'hr.holidays.status'
    _description = 'Leave Type'

    def get_days(self, cr, uid, ids, employee_id, context=None):
        result = dict((id, dict(max_leaves=0, leaves_taken=0, remaining_leaves=0,
                                virtual_remaining_leaves=0)) for id in ids)
        
        acc_fy = self.pool.get('account.fiscalyear')
        now_date=datetime.now().strftime ("%Y-%m-%d")
        fys = self.pool['account.fiscalyear'].search(cr, uid, [('date_stop','>=',time.strftime("%Y-%m-%d")),('date_start','<=',time.strftime("%Y-%m-%d")) ])
        
        holiday_ids = self.pool['hr.holidays'].search(cr, uid, [('employee_id', '=', employee_id),
                                                                ('state', 'in', ['confirm', 'validate1', 'validate']),
                                                                ('holiday_status_id', 'in', ids),
                                                                ('expiry_date', '>=', now_date)
                                                                ], context=context)
#         line1 = self.pool['hr.holidays'].search(cr, uid, [('expiry_date','>=',time.strftime("%Y-%m-%d"))])
#         line2 = self.pool['hr.holidays'].search(cr, uid, [('date_to','<=',time.strftime("%Y-%m-%d"))])
#         final_line = line1 + line2
        for holiday in self.pool['hr.holidays'].browse(cr, uid, holiday_ids, context=context):
            status_dict = result[holiday.holiday_status_id.id]
            if holiday.type == 'add':
                status_dict['virtual_remaining_leaves'] += holiday.number_of_days_temp
                if holiday.state == 'validate':
                    status_dict['max_leaves'] += holiday.number_of_days_temp
                    status_dict['remaining_leaves'] += holiday.number_of_days_temp
            elif holiday.type == 'remove':  # number of days is negative
                status_dict['virtual_remaining_leaves'] -= holiday.number_of_days_temp
                if holiday.state == 'validate':
                    status_dict['leaves_taken'] += holiday.number_of_days_temp
                    status_dict['remaining_leaves'] -= holiday.number_of_days_temp
        return result

   
   
    