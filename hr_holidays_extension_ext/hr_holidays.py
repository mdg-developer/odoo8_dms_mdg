# -*- coding:utf-8 -*-
#
#
#    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    Copyright (c) 2005-2006 Axelor SARL. (http://www.axelor.com)
#    and 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc

from openerp import tools
from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as OE_DTFORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT
from openerp.tools.translate import _


class hr_holidays_status(osv.Model):

    _inherit = 'hr.holidays.status'

    _columns = {
        'ex_rest_days': fields.boolean('Exclude Rest Days',
                                       help="If enabled, the employee's day off is skipped in leave days calculation."),
        'ex_public_holidays': fields.boolean('Exclude Public Holidays',
                                             help="If enabled, public holidays are skipped in leave days calculation."),
    }


class hr_holidays(osv.osv):

    _name = 'hr.holidays'
    _inherit = ['hr.holidays', 'ir.needaction_mixin']
    def _get_can_reset(self, cr, uid, ids, name, arg, context=None):
        """User can reset a leave request if it is its own leave request or if
        he is an Hr Manager. """
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        group_hr_manager_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'base', 'group_hr_manager')[1]
        if group_hr_manager_id in [g.id for g in user.groups_id]:
            return dict.fromkeys(ids, True)
        result = dict.fromkeys(ids, False)
        for holiday in self.browse(cr, uid, ids, context=context):
            if holiday.employee_id and holiday.employee_id.user_id and holiday.employee_id.user_id.id == uid:
                result[holiday.id] = True
        return result
    _columns = {
        'real_days': fields.float('Total Days', digits=(16, 1)),
        'rest_days': fields.float('Rest Days', digits=(16, 1)),
        'public_holiday_days': fields.float('Public Holidays', digits=(16, 1)),
        'return_date': fields.char('Return Date', size=32),
        'can_reset': fields.function(
            _get_can_reset,
            type='boolean'),
    }

    def _employee_get(self, cr, uid, context=None):

        if context == None:
            context = {}

        # If the user didn't enter from "My Leaves" don't pre-populate Employee
        # field
        import logging
        _l = logging.getLogger(__name__)
        _l.warning('context: %s', context)
        if not context.get('search_default_my_leaves', False):
            return False

        ids = self.pool.get('hr.employee').search(
            cr, uid, [('user_id', '=', uid)], context=context)
        if ids:
            return ids[0]
        return False

    def _days_get(self, cr, uid, context=None):

        if context == None:
            context = {}

        date_from = context.get('default_date_from')
        date_to = context.get('default_date_to')
        if date_from and date_to:
            delta = datetime.strptime(date_to, OE_DTFORMAT) - datetime.strptime(date_from, OE_DTFORMAT)
            return (delta.days + 1 and delta.days + 1 or 1)
        return False

    _defaults = {
        'employee_id': _employee_get,
        'number_of_days_temp': _days_get,
    }

    _order = 'date_from asc, type desc'

    def _needaction_domain_get(self, cr, uid, context=None):

        users_obj = self.pool.get('res.users')
        domain = []

        if users_obj.has_group(cr, uid, 'base.group_hr_manager'):
            domain = [('state', 'in', ['draft', 'confirm'])]
            return domain

        elif users_obj.has_group(cr, uid, 'hr_holidays_extension.group_hr_leave'):
            domain = [('state', 'in', ['confirm']), (
                'employee_id.user_id', '!=', uid)]
            return domain

        return False

    def onchange_bynumber(self, cr, uid, ids, no_days, date_from, employee_id, holiday_status_id, context=None):
        """
        Update the dates based on the number of days requested.
        """

        ee_obj = self.pool.get('hr.employee')
        holiday_obj = self.pool.get('hr.holidays.public')
        sched_tpl_obj = self.pool.get('hr.schedule.template')
        sched_detail_obj = self.pool.get('hr.schedule.detail')
        result = {'value': {}}

        if not no_days or not date_from or not employee_id:
            return result

        user = self.pool.get('res.users').browse(cr, uid, uid)
        if user and user.tz:
            local_tz = timezone(user.tz)
        else:
            local_tz = timezone('Africa/Addis_Ababa')

        dt = datetime.strptime(date_from, OE_DTFORMAT)
        employee = ee_obj.browse(cr, uid, employee_id, context=context)
        if holiday_status_id:
            hs_data = self.pool.get(
                'hr.holidays.status').read(cr, uid, holiday_status_id,
                                           ['ex_rest_days', 'ex_public_holidays'],
                                           context=context)
        else:
            hs_data = {}
        ex_rd = hs_data.get('ex_rest_days', False)
        ex_ph = hs_data.get('ex_public_holidays', False)

        # Get rest day and the schedule start time on the date the leave begins
        #
        rest_days = []
        times = tuple()
        if ex_rd:
            if employee.contract_id and employee.contract_id.schedule_template_id:
                rest_days = sched_tpl_obj.get_rest_days(cr, uid,
                                                        employee.contract_id.schedule_template_id.id,
                                                        context=context)
                times = sched_detail_obj.scheduled_begin_end_times(
                    cr, uid, employee.id,
                    employee.contract_id.id, dt,
                    context=context)
        if len(times) > 0:
            utcdtStart = times[0][0]
        else:
            dtStart = local_tz.localize(
                datetime.strptime(dt.strftime(OE_DFORMAT) + ' 00:00:00', OE_DTFORMAT), is_dst=False)
            utcdtStart = dtStart.astimezone(utc)

        count_days = no_days
        real_days = 1
        ph_days = 0
        r_days = 0
        next_dt = dt
        while count_days > 1:
            public_holiday = holiday_obj.is_public_holiday(
                cr, uid, next_dt.date(), context=context)
            public_holiday = (public_holiday and ex_ph)
            rest_day = (next_dt.weekday() in rest_days and ex_rd)
            next_dt += timedelta(days=+1)
            if public_holiday or rest_day:
                if public_holiday:
                    ph_days += 1
                elif rest_day:
                    r_days += 1
                real_days += 1
                continue
            else:
                count_days -= 1
                real_days += 1
        while (next_dt.weekday() in rest_days and ex_rd) or (holiday_obj.is_public_holiday(cr, uid, next_dt.date(), context=context) and ex_ph):
            if holiday_obj.is_public_holiday(cr, uid, next_dt.date(), context=context):
                ph_days += 1
            elif next_dt.weekday() in rest_days:
                r_days += 1
            next_dt += timedelta(days=1)
            real_days += 1

        # Set end time based on schedule
        #
        times = sched_detail_obj.scheduled_begin_end_times(
            cr, uid, employee.id,
            employee.contract_id.id, next_dt,
            context=context)
        if len(times) > 0:
            utcdtEnd = times[-1][1]
        else:
            dtEnd = local_tz.localize(
                datetime.strptime(next_dt.strftime(OE_DFORMAT) + ' 23:59:59', OE_DTFORMAT), is_dst=False)
            utcdtEnd = dtEnd.astimezone(utc)

        result['value'].update({'department_id': employee.department_id.id,
                                # 'date_from': utcdtStart.strftime(OE_DTFORMAT),
                                # 'date_to': utcdtEnd.strftime(OE_DTFORMAT),
                                'rest_days': r_days,
                                'public_holiday_days': ph_days,
                                'real_days': real_days})
        return result

    def onchange_enddate(self, cr, uid, ids, employee_id, date_to, holiday_status_id, context=None):

        ee_obj = self.pool.get('hr.employee')
        holiday_obj = self.pool.get('hr.holidays.public')
        sched_tpl_obj = self.pool.get('hr.schedule.template')
        res = {'value': {'return_date': False}}

        if not employee_id or not date_to:
            return res

        if holiday_status_id:
            hs_data = self.pool.get(
                'hr.holidays.status').read(cr, uid, holiday_status_id,
                                           ['ex_rest_days', 'ex_public_holidays'],
                                           context=context)
        else:
            hs_data = {}
        ex_rd = hs_data.get('ex_rest_days', False)
        ex_ph = hs_data.get('ex_public_holidays', False)

        rest_days = []
        if ex_rd:
            ee = ee_obj.browse(cr, uid, employee_id, context=context)
            if ee.contract_id and ee.contract_id.schedule_template_id:
                rest_days = sched_tpl_obj.get_rest_days(cr, uid,
                                                        ee.contract_id.schedule_template_id.id,
                                                        context=context)

        dt = datetime.strptime(date_to, OE_DTFORMAT)
        return_date = dt + timedelta(days=+1)
        while (return_date.weekday() in rest_days and ex_rd) or (holiday_obj.is_public_holiday(cr, uid, return_date.date(), context=context) and ex_ph):
            return_date += timedelta(days=1)
        res['value']['return_date'] = return_date.strftime('%B %d, %Y')
        return res

    def create(self, cr, uid, vals, context=None):

        att_obj = self.pool.get('hr.attendance')
        if vals.get('date_from', False) and vals.get('date_to', False) and (not vals.get('type', False) or vals.get('type', 'x') == 'remove') and vals.get('holiday_type', 'x') == 'employee':
            att_ids = att_obj.search(
                cr, uid, [('employee_id', '=', vals['employee_id']),
                          ('name', '>=', vals[
                              'date_from']),
                          ('name', '<=', vals['date_to'])],
                context=context)
            if len(att_ids) > 0:
                raise osv.except_osv(_('Warning'),
                                     _('There is already one or more attendance records for the date you have chosen.'))

        return super(hr_holidays, self).create(cr, uid, vals, context=context)

    def holidays_first_validate(self, cr, uid, ids, context=None):

        self._check_validate(cr, uid, ids, context=context)
        return super(hr_holidays, self).holidays_first_validate(cr, uid, ids, context=context)

    def holidays_validate(self, cr, uid, ids, context=None):

        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False
        self.write(cr, uid, ids, {'state':'validate'})
        data_holiday = self.browse(cr, uid, ids)
        return_date = data_holiday['return_date']
        date_from = data_holiday['date_from']
        emp_id = data_holiday['employee_id'].id
        if return_date and emp_id:
            try:
                self.restart_probation(cr, uid, emp_id, return_date, date_from, context=context)
            except Exception, e:
                raise osv.except_osv(_('Invalid Action!'), _('you must cancel it first.%s' % e))
        for record in data_holiday:
            if record.double_validation:
                self.write(cr, uid, [record.id], {'manager_id2': manager})
            else:
                self.write(cr, uid, [record.id], {'manager_id': manager})
            if record.holiday_type == 'employee' and record.type == 'remove':
                meeting_obj = self.pool.get('calendar.event')
                meeting_vals = {
                    'name': record.name or _('Leave Request'),
                    'categ_ids': record.holiday_status_id.categ_id and [(6, 0, [record.holiday_status_id.categ_id.id])] or [],
                    'duration': record.number_of_days_temp * 8,
                    'description': record.notes,
                    'user_id': record.user_id.id,
                    'start': record.date_from,
                    'stop': record.date_to,
                    'allday': False,
                    'state': 'open',  # to block that meeting date in the calendar
                    'class': 'confidential'
                }   
                # Add the partner_id (if exist) as an attendee             
                if record.user_id and record.user_id.partner_id:
                    meeting_vals['partner_ids'] = [(4, record.user_id.partner_id.id)]
                    
                ctx_no_email = dict(context or {}, no_email=True)
                meeting_id = meeting_obj.create(cr, uid, meeting_vals, context=ctx_no_email)
                self._create_resource_leave(cr, uid, [record], context=context)
                self.write(cr, uid, ids, {'meeting_id': meeting_id})
            elif record.holiday_type == 'category':
                emp_ids = obj_emp.search(cr, uid, [('category_ids', 'child_of', [record.category_id.id])])
                leave_ids = []
                print 'emp_ids', emp_ids
                number_of_days_temp = record.number_of_days_temp
                status_id = record.holiday_status_id.id
                
                for emp in obj_emp.browse(cr, uid, emp_ids):
                    vals = {
                        'name': record.name,
                        'type': record.type,
                        'holiday_type': 'employee',
                        'holiday_status_id': record.holiday_status_id.id,
                        'date_from': record.date_from,
                        'date_to': record.date_to,
                        'notes': record.notes,
                        'number_of_days_temp': record.number_of_days_temp,
                        'parent_id': record.id,
                        'employee_id': emp.id
                    }
                    cr.execute("select id from hr_holidays where number_of_days_temp=%s and holiday_status_id= %s and holiday_type= 'employee' and employee_id= %s", (number_of_days_temp, status_id, emp.id,))
                    id = cr.fetchone()  
                    print 'id', id
                    if id is None:       
                        leave_ids.append(self.create(cr, uid, vals, context=None))


                for leave_id in leave_ids:
                    # TODO is it necessary to interleave the calls?
                    for sig in ('confirm', 'validate', 'second_validate'):
                        self.signal_workflow(cr, uid, [leave_id], sig)
        return True
    
    #   This is for restart probation period by leave
    def restart_probation(self, cr, uid, emp_id, return_date, date_from, context):
        emp_id = emp_id
        return_date = return_date
        date_end = leave_control = None
        contract_obj = self.pool.get('hr.contract')
        contract_id = contract_obj.search(cr, uid, [('employee_id', '=', emp_id)])
        res = contract_obj.browse(cr, uid, contract_id, context=context)
        if res:
            date_end = datetime.strptime(res.trial_date_end, '%Y-%m-%d')
            leave_control = res.leave_control
        #### Condition for "In Probation" or "Permanent"    
        if leave_control == True:
            if contract_id and  datetime.strptime(date_from, '%Y-%m-%d %H:%M:%S') <= date_end:    
                trial_start_date = trial_end_date = None  # One
                trial_start_date = datetime.strptime(return_date, '%B %d, %Y')
                trial_end_date = trial_start_date + relativedelta(months=3)
                #### Update to hr_Contract Table 
                cr.execute('update hr_contract set trial_date_start = %s ,trial_date_end = %s where employee_id =%s', (trial_start_date, trial_end_date, emp_id,))
        return True
    
    def _check_validate(self, cr, uid, ids, context=None):
 
        users_obj = self.pool.get('res.users')
 
        if not users_obj.has_group(cr, uid, 'base.group_hr_manager'):
            for leave in self.browse(cr, uid, ids, context=context):
                if leave.employee_id.user_id.id == uid:
                    raise osv.except_osv(
                        _('Warning!'), _('You cannot approve your own leave:\nHoliday Type: %s\nEmployee: %s') % 
                        (leave.holiday_status_id.name, leave.employee_id.name))
        return


class hr_attendance(osv.Model):

    _name = 'hr.attendance'
    _inherit = 'hr.attendance'

    def create(self, cr, uid, vals, context=None):

        if vals.get('name', False):
            lv_ids = self.pool.get(
                'hr.holidays').search(cr, uid, [('employee_id', '=', vals['employee_id']),
                                                ('type', '=', 'remove'),
                                                ('date_from', '<=', vals[
                                                    'name']),
                                                ('date_to', '>=', vals[
                                                    'name']),
                                                ('state', 'not in', ['cancel', 'refuse'])],
                                      context=context)
            if len(lv_ids) > 0:
                ee_data = self.pool.get(
                    'hr.employee').read(cr, uid, vals['employee_id'], ['name'],
                                        context=context)
                raise osv.except_osv(_('Warning'),
                                     _('There is already one or more leaves recorded for the date you have chosen:\nEmployee: %s\nDate: %s' % (ee_data['name'], vals['name'])))

        return super(hr_attendance, self).create(cr, uid, vals, context=context)
