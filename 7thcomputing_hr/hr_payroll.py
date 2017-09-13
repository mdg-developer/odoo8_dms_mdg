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

class policy_line_ot(osv.Model):

    _name = 'hr.policy.line.late'
    _inherit='hr.policy.line.late'

    _columns = {

        'sat_late': fields.boolean('Saturday late'),
        'type': fields.selection([('daily', 'Daily'),('break_over','Break Over 45min'),('break_absence','Break In,Break Out Absence')],
                                 'Type', required=True),
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
class hr_attendance(osv.osv):

    _name = 'hr.attendance'
    _inherit = 'hr.attendance'

    def _calculate_rollover(self, utcdt, rollover_hours):

        # XXX - assume time part of utcdt is already set to midnight
        return utcdt + timedelta(hours=int(rollover_hours))

    def punches_list_init(self, cr, uid, employee_id, pps_template, dFrom, dTo, context=None):
        '''Returns a dict containing a key for each day in range dFrom - dToday and a
        corresponding tuple containing two list: in punches, and the corresponding out punches'''

        res = []

        # Convert datetime to tz aware datetime according to tz in pay period schedule,
        # then to UTC, and then to naive datetime for comparison with values in db.
        #
        # Also, includue records 48 hours previous to and 48 hours after the desired
        # dates so that any requests for rollover, sessions, etc are can be satisfied
        #
        dtFrom = datetime.strptime(
            dFrom.strftime(OE_DATEFORMAT) + ' 00:00:00', OE_DATETIMEFORMAT)
        dtFrom += timedelta(hours=-48)
        dtTo = datetime.strptime(
            dTo.strftime(OE_DATEFORMAT) + ' 00:00:00', OE_DATETIMEFORMAT)
        dtTo += timedelta(hours=+48)
        utcdtFrom = timezone(pps_template.tz).localize(
            dtFrom, is_dst=False).astimezone(utc)
        utcdtTo = timezone(pps_template.tz).localize(
            dtTo, is_dst=False).astimezone(utc)
        utcdtDay = utcdtFrom
        utcdtDayEnd = utcdtTo + timedelta(days=+1, seconds=-1)
        ndtDay = utcdtDay.replace(tzinfo=None)
        ndtDayEnd = utcdtDayEnd.replace(tzinfo=None)

        ids = self.search(cr, uid, [('employee_id', '=', employee_id),
                                    '&', (
                                        'name', '>=', ndtDay.strftime(OE_DATETIMEFORMAT)),
                                    ('name', '<=', ndtDayEnd.strftime(OE_DATETIMEFORMAT))],
                          order='name', context=context)

        for a in self.browse(cr, uid, ids, context=context):
            res.append((a.action, a.name))

        return res

    def punches_list_search(self, cr, uid, ndtFrom, ndtTo, punches_list, context=None):

        res = []
        for action, name in punches_list:
            ndtName = datetime.strptime(name, OE_DATETIMEFORMAT)
            if ndtName >= ndtFrom and ndtName <= ndtTo:
                res.append((action, name))
        return res

    def _get_normalized_punches(self, cr, uid, employee_id, pps_template, dDay, punches_list, context=None):
        '''Returns a tuple containing two lists: in punches, and corresponding out punches'''

        #
        # We assume that:
        #    - No dangling sign-in or sign-out
        #

        # Convert datetime to tz aware datetime according to tz in pay period schedule,
        # then to UTC, and then to naive datetime for comparison with values in db.
        #
        dt = datetime.strptime(
            dDay.strftime(OE_DATEFORMAT) + ' 00:00:00', OE_DATETIMEFORMAT)
        utcdtDay = timezone(pps_template.tz).localize(
            dt, is_dst=False).astimezone(utc)
        utcdtDayEnd = utcdtDay + timedelta(days=+1, seconds=-1)
        ndtDay = utcdtDay.replace(tzinfo=None)
        ndtDayEnd = utcdtDayEnd.replace(tzinfo=None)
        my_list = self.punches_list_search(
            cr, uid, ndtDay, ndtDayEnd, punches_list, context=context)
        if len(my_list) == 0:
            return [], []

        # We are assuming attendances are normalized: (in, out, in, out, ...)
        sin = []
        sout = []
        for action, name in my_list:
            if action == 'sign_in':
                sin.append(name)
            elif action == 'sign_out':
                sout.append(name)

        if len(sin) == 0 and len(sout) == 0:
            return [], []

        # CHECKS AT THE START OF THE DAY
        # Remove sessions that would have been included in yesterday's
        # attendance.

        # We may have a a session *FROM YESTERDAY* that crossed-over into
        # today. If it is greater than the maximum continuous hours allowed into
        # the next day (as configured in the pay period schedule), then count
        # only the difference between the actual and the maximum continuous
        # hours.
        #
        dtRollover = (self._calculate_rollover(
            utcdtDay, pps_template.ot_max_rollover_hours)).replace(tzinfo=None)
        if (len(sout) - len(sin)) == 0:

            if len(sout) > 0:
                dtSout = datetime.strptime(sout[0], OE_DATETIMEFORMAT)
                dtSin = datetime.strptime(sin[0], OE_DATETIMEFORMAT)
                if dtSout > dtRollover and (dtSout < dtSin):
                    sin = [dtRollover.strftime(OE_DATETIMEFORMAT)] + sin
                elif dtSout < dtSin:
                    sout = sout[1:]
                    # There may be another session that starts within the
                    # rollover period
                    if dtSin < dtRollover and float((dtSin - dtSout).seconds) / 60.0 >= pps_template.ot_max_rollover_gap:
                        sin = sin[1:]
                        sout = sout[1:]
            else:
                return [], []
        elif (len(sout) - len(sin)) == 1:
            dtSout = datetime.strptime(sout[0], OE_DATETIMEFORMAT)
            if dtSout > dtRollover:
                sin = [dtRollover.strftime(OE_DATETIMEFORMAT)] + sin
            else:
                sout = sout[1:]
                # There may be another session that starts within the rollover
                # period
                dtSin = False
                if len(sin) > 0:
                    dtSin = datetime.strptime(sin[0], OE_DATETIMEFORMAT)
                if dtSin and dtSin < dtRollover and float((dtSin - dtSout).seconds) / 60.0 >= pps_template.ot_max_rollover_gap:
                    sin = sin[1:]
                    sout = sout[1:]

        # If the first sign-in was within the rollover gap *AT* midnight check to
        # see if there are any sessions within the rollover gap before it.
        #
        if len(sout) > 0:
            ndtSin = datetime.strptime(sin[0], OE_DATETIMEFORMAT)
            if (ndtSin - timedelta(minutes=pps_template.ot_max_rollover_gap)) <= ndtDay:
                my_list4 = self.punches_list_search(
                    cr, uid, ndtDay + timedelta(hours=-24),
                    ndtDay + timedelta(seconds=-1), punches_list, context=context)
                if len(my_list4) > 0:
                    if (my_list4[-1].action == 'sign_out'):
                        ndtSout = datetime.strptime(
                            my_list4[-1].name, OE_DATETIMEFORMAT)
                        if (ndtSin <= ndtSout + timedelta(minutes=pps_template.ot_max_rollover_gap)):
                            sin = sin[1:]
                            sout = sout[1:]

        # CHECKS AT THE END OF THE DAY
        # Include sessions from tomorrow that should be included in today's
        # attendance.

        # We may have a session that crosses the midnight boundary. If so, add it to today's
        # session.
        #
        dtRollover = (self._calculate_rollover(ndtDay + timedelta(days=1),
                                               pps_template.ot_max_rollover_hours)).replace(tzinfo=None)
        if (len(sin) - len(sout)) == 1:

            my_list2 = self.punches_list_search(
                cr, uid, ndtDayEnd + timedelta(seconds=+1),
                ndtDayEnd + timedelta(days=1), punches_list, context=context)
            if len(my_list2) == 0:
                name = self.pool.get('hr.employee').read(
                    cr, uid, employee_id, ['name'])['name']
                raise osv.except_osv(_('Attendance Error!'),
                                     _('There is not a final sign-out record for %s on %s') % (name, dDay))

            action, name = my_list2[0]
            if action == 'sign_out':
                dtSout = datetime.strptime(name, OE_DATETIMEFORMAT)
                if dtSout > dtRollover:
                    sout.append(dtRollover.strftime(OE_DATETIMEFORMAT))
                else:
                    sout.append(name)
                    # There may be another session within the OT max. rollover
                    # gap
                    if len(my_list2) > 2 and my_list2[1][0] == 'sign_in':
                        dtSin = datetime.strptime(name, OE_DATETIMEFORMAT)
                        if float((dtSin - dtSout).seconds) / 60.0 < pps_template.ot_max_rollover_gap:
                            sin.append(my_list2[1][1])
                            sout.append(my_list2[2][1])

            else:
                name = self.pool.get('hr.employee').read(
                    cr, uid, employee_id, ['name'])['name']
                raise osv.except_osv(_('Attendance Error!'),
                                     _('There is a sign-in with no corresponding sign-out for %s on %s') % (name, dDay))

        # If the last sign-out was within the rollover gap *BEFORE* midnight check to
        # see if there are any sessions within the rollover gap after it.
        #
        if len(sout) > 0:
            ndtSout = datetime.strptime(sout[-1], OE_DATETIMEFORMAT)
            if (ndtDayEnd - timedelta(minutes=pps_template.ot_max_rollover_gap)) <= ndtSout:
                my_list3 = self.punches_list_search(
                    cr, uid, ndtDayEnd + timedelta(seconds=+1),
                    ndtDayEnd + timedelta(hours=+24), punches_list, context=context)
                if len(my_list3) > 0:
                    action, name = my_list3[0]
                    ndtSin = datetime.strptime(name, OE_DATETIMEFORMAT)
                    if (ndtSin <= ndtSout + timedelta(minutes=pps_template.ot_max_rollover_gap)) and action == 'sign_in':
                        sin.append(name)
                        sout.append(my_list3[1][1])

        return sin, sout

    def _on_day(self, cr, uid, contract, dDay, punches_list=None, context=None):
        '''Return two lists: the first is sign-in times, and the second is corresponding sign-outs.'''

        if punches_list == None:
            punches_list = self.punches_list_init(
                cr, uid, contract.employee_id.id, contract.pps_id,
                dDay, dDay, context)

        sin, sout = self._get_normalized_punches(
            cr, uid, contract.employee_id.id, contract.pps_id,
            dDay, punches_list, context=context)
        if len(sin) != len(sout):
            raise osv.except_osv(
                _('Number of Sign-in and Sign-out records do not match!'),
                _('Employee: %s\nSign-in(s): %s\nSign-out(s): %s') % (contract.employee_id.name, sin, sout))

        return sin, sout

    def punch_names_on_day(self, cr, uid, contract, dDay, punches_list=None, context=None):
        '''Return a list of tuples containing in and corresponding out punches for the day.'''

        sin, sout = self._on_day(
            cr, uid, contract, dDay, punches_list=punches_list, context=context)

        res = []
        for i in range(0, len(sin)):
            res.append((sin[i], sout[i]))

        return res

    def punch_ids_on_day(self, cr, uid, contract, dDay, punches_list=None, context=None):
        '''Return a list of database ids of punches for the day.'''

        sin, sout = self._on_day(
            cr, uid, contract, dDay, punches_list=punches_list, context=context)

        names = []
        for i in range(0, len(sin)):
            names.append(sin[i])
            names.append(sout[i])

        return self.search(
            cr, uid, [('employee_id', '=', contract.employee_id.id),
                      ('name', 'in', names)],
            order='name', context=context)

    def total_hours_on_day(self, cr, uid, contract, dDay, punches_list=None, context=None):
        '''Calculate the number of hours worked on specified date.'''

        sin, sout = self._on_day(
            cr, uid, contract, dDay, punches_list=punches_list, context=context)

        worked_hours = 0
        for i in range(0, len(sin)):
            start = datetime.strptime(sin[i], '%Y-%m-%d %H:%M:%S')
            end = datetime.strptime(sout[i], '%Y-%m-%d %H:%M:%S')
            worked_hours += float((end - start).seconds) / 60.0 / 60.0

        return worked_hours
    
    def late_hours_on_day(
        self, cr, uid, contract, dtDay, active_after, begin, stop, tz,
            punches_list=None, context=None):
        '''Calculate the number of hours worked between begin and stop hours, but
        after active_after hours past the beginning of the first sign-in on specified date.'''

        # Since OpenERP stores datetime in db as UTC, but in naive format we have to do
        # the following to compare our partial time to the time in db:
        #    1. Make our partial time into a naive datetime
        #    2. Localize the naive datetime to the timezone specified by our caller
        #    3. Convert our localized datetime to UTC
        #    4. Convert our UTC datetime back into naive datetime format
        #
        dtBegin = datetime.strptime(
            dtDay.strftime(OE_DATEFORMAT) + ' ' + begin + ':00', OE_DATETIMEFORMAT)
        dtStop = datetime.strptime(
            dtDay.strftime(OE_DATEFORMAT) + ' ' + stop + ':00', OE_DATETIMEFORMAT)
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
            if start > dtStop:
               continue;
            if worked_hours == 0 and start > dtBegin:
                worked_hours += float((start - dtBegin).seconds) / 60.0 / 60.0

        if worked_hours == 0:
            return 0
        elif lead_hours >= active_after:
            return worked_hours

        return max(0, (worked_hours + lead_hours) - active_after)
    def late_hours_on_pay_day(

        self, cr, uid, contract, dtDay, active_after, begin, stop,pay_day,tz,

            punches_list=None, context=None):

        '''Calculate the number of hours worked between begin and stop hours, but

        after active_after hours past the beginning of the first sign-in on specified date.'''



        # Since OpenERP stores datetime in db as UTC, but in naive format we have to do

        # the following to compare our partial time to the time in db:

        #    1. Make our partial time into a naive datetime

        #    2. Localize the naive datetime to the timezone specified by our caller

        #    3. Convert our localized datetime to UTC

        #    4. Convert our UTC datetime back into naive datetime format

        #

        dtBegin = datetime.strptime(dtDay.strftime(OE_DATEFORMAT) + ' ' + begin + ':00', OE_DATETIMEFORMAT)

        dtStop = datetime.strptime(dtDay.strftime(OE_DATEFORMAT) + ' ' + stop + ':00', OE_DATETIMEFORMAT)

        if dtStop <= dtBegin:

           dtStop += timedelta(days=1)

        utcdtBegin = timezone(tz).localize(dtBegin, is_dst=False).astimezone(utc)

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

            start_date = start.date()

            pay_date=datetime.strptime(pay_day, '%Y-%m-%d')

            p_date = pay_date.date()

            print 'datedatedate...................',p_date,start_date

            if start > dtStop:

                continue;

            print 'datestartlll..................',start,dtBegin

           

            if worked_hours == 0 and start > dtBegin and p_date==start_date:

                worked_hours += float((start - dtBegin).seconds) / 60.0 / 60.0



        if worked_hours == 0:

            return 0

        elif lead_hours >= active_after:

            return worked_hours

        return max(0, (worked_hours + lead_hours) - active_after)        
    def partial_hours_on_day(
        self, cr, uid, contract, dtDay, active_after, begin, stop, morning, tz,
            punches_list=None, context=None):
        print "In real calculation of partial work hour for other ========================="
      
                                   
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
            print 'Final work hour is----------', worked_hours
        return max(0, (worked_hours + lead_hours) - active_after)

    
    def partial_hours_on_day_by_specific_date_and_hours(
        self, cr, uid, contract, dtDay, active_after, begin, stop, morning, working_hours_on_day, ot_day, specif_working_hr, tz,
            punches_list=None, context=None):
        
        print "In real calculation of partial work hour for Factory Shift otday , begin , stop===============" , ot_day , begin, stop
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
        
        # # checking whether sign in date and sign out date equal or not
#         new_sin = sin.date()
#         new_sout = sout.date()
#         print 'Checking attendance data only date equal or not is -----',new_sin , new_sout

        
        worked_hours = 0
        tmp_worked_hours = 0
        lead_hours = 0
        for i in range(0, len(sin)):
            start = datetime.strptime(sin[i], '%Y-%m-%d %H:%M:%S')
            end = datetime.strptime(sout[i], '%Y-%m-%d %H:%M:%S')
            
            print "Start and end is-----" , start, end
            
            start_date = start.date()
            end_date = end.date()
            
            # must define end and OT shall end shall be within the boundary
            print 'int(start.weekday()) ======' , int(start.weekday())
            print 'int(ot_day) ======' , int(ot_day) 
            cr.execute('''select worked_hours from hr_attendance where action='sign_out' and name= %s''', ([end]))
            working_hours = cr.fetchone() 
            working_hours_on_day=working_hours[0]
            if(int(start.weekday()) == int(ot_day)):
              print 'working_hours_on_day-----------type----',type(working_hours_on_day)
              print 'working_hours_on_day---------------',working_hours_on_day

              if working_hours_on_day:
                print "kkkkkkkkkkkkkkkkk===============",working_hours_on_day                            
                if morning == False and end and dtStop and end > dtStop:
                    continue;
                 
     
                if ot_day and  start_date != end_date :
                            tmp_worked_hours = float((end - start).seconds) / 60.0 / 60.0
                            if tmp_worked_hours  and specif_working_hr:
                                tmp_worked_hours = int(specif_working_hr) - tmp_worked_hours;
                            else:
                                tmp_worked_hours = 0;
                worked_hours += tmp_worked_hours 
                print 'tmp_worked_hour , start , end =========', tmp_worked_hours , start , end
        
     
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
                    tmp_worked_hours = float((end - start).seconds) / 60.0 / 60.0
                    print tmp_worked_hours
                    start_date = start.date()
                    end_date = end.date()
                    if ot_day and tmp_worked_hours:
                        if int(start.weekday()) != int(ot_day):  # monday, =0 sun =6
                            tmp_worked_hours = 0;
                        else:
     
                            if morning == False and specif_working_hr and start_date == end_date:
                                if  tmp_worked_hours > int(specif_working_hr):
                                    tmp_worked_hours = tmp_worked_hours - int(specif_working_hr)
                                else:
                                    tmp_worked_hours = 0;
                            elif morning == True and working_hours_on_day != 12.0 and working_hours_on_day != None:          
                                 if working_hours_on_day <= 12.0 and working_hours_on_day == 11:
                                    tmp_worked_hours = 3;
                                 elif working_hours_on_day <= 11.0 and working_hours_on_day == 10:
                                    tmp_worked_hours = 2;
                                 else:
                                     tmp_worked_hours = 0;                                    
                                 print 'Alter hour ========', tmp_worked_hours                                                  
                                 
                            elif morning == True:
                                 tmp_worked_hours = int(specif_working_hr)
                            else:
                                 tmp_worked_hours = 0
                             
                        worked_hours += tmp_worked_hours
                    print 'Ot day, Final work hour shown on payslip is+++++++++++++++++++', ot_day, worked_hours
              
 
            elif worked_hours > 0 and start < dtStop:
                if end > dtStop:
                    end = dtStop
                tmp_worked_hours = float((end - start).seconds) / 60.0 / 60.0
                if ot_day and tmp_worked_hours:
                    if int(start.weekday()) != int(ot_day):  # monday, =0 sun =6
                        tmp_worked_hours = 0;
                    else:
                        if specif_working_hr:  # extra specific hours
                            if  int(specif_working_hr) > tmp_worked_hours:
                                tmp_worked_hours = tmp_worked_hours - int(specif_working_hr)
                            else:
                                tmp_worked_hours = 0;
                worked_hours += tmp_worked_hours
                 
        if worked_hours == 0:
            return 0
        elif lead_hours >= active_after:
            return worked_hours
        return max(0, (worked_hours + lead_hours) - active_after)           
class hr_payslip(osv.osv):

    _name = 'hr.payslip'
    _inherit = 'hr.payslip'
    
    def get_worked_day_lines(self, cr, uid, contract_ids, date_from, date_to, context=None):
        """
        @param contract_ids: list of contract id
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """

        sched_tpl_obj = self.pool.get('hr.schedule.template')
        sched_obj = self.pool.get('hr.schedule')
        sched_detail_obj = self.pool.get('hr.schedule.detail')
        ot_obj = self.pool.get('hr.policy.ot')
        late_obj = self.pool.get('hr.policy.late')
        presence_obj = self.pool.get('hr.policy.presence')
        absence_obj = self.pool.get('hr.policy.absence')
        holiday_obj = self.pool.get('hr.holidays.public')

        day_from = datetime.strptime(date_from, "%Y-%m-%d").date()
        day_to = datetime.strptime(date_to, "%Y-%m-%d").date()
        nb_of_days = (day_to - day_from).days + 1

        # Initialize list of public holidays. We only need to calculate it once during
        # the lifetime of this object so attach it directly to it.
        #
        try:
            public_holidays_list = self._mtm_public_holidays_list
        except AttributeError:
            self._mtm_public_holidays_list = self.holidays_list_init(
                cr, uid, day_from, day_to,
                context=context)
            public_holidays_list = self._mtm_public_holidays_list
        
        def get_late_policies(policy_group_id, day, data):
            if data == None or not data['_reuse']:
                data = {
                    'policy': None,
                    'daily': None,
                    '_reuse': False,
                }
            elif data['_reuse']:
                return data
            late_policy = self._get_late_policy(policy_group_id, day)
            daily_late = late_policy and len(
                late_obj.daily_codes(cr, uid, late_policy.id, context=context)) > 0 or None
            data['policy'] = late_policy
            data['daily'] = daily_late

            return data
         

         
        def get_ot_policies(policy_group_id, day, data):

            if data == None or not data['_reuse']:
                data = {
                    'policy': None,
                    'daily': None,
                    'restday2': None,
                    'restday': None,
                    'weekly': None,
                    'holiday': None,
                    '_reuse': False,
                }
            elif data['_reuse']:
                return data

            ot_policy = self._get_ot_policy(policy_group_id, day)
            daily_ot = ot_policy and len(
                ot_obj.daily_codes(cr, uid, ot_policy.id, context=context)) > 0 or None
            restday2_ot = ot_policy and len(ot_obj.restday2_codes(
                cr, uid, ot_policy.id, context=context)) > 0 or None
            restday_ot = ot_policy and len(ot_obj.restday_codes(
                cr, uid, ot_policy.id, context=context)) > 0 or None
            weekly_ot = ot_policy and len(
                ot_obj.weekly_codes(cr, uid, ot_policy.id, context=context)) > 0 or None
            holiday_ot = ot_policy and len(ot_obj.holiday_codes(
                cr, uid, ot_policy.id, context=context)) > 0 or None

            data['policy'] = ot_policy
            data['daily'] = daily_ot
            data['restday2'] = restday2_ot
            data['restday'] = restday_ot
            data['weekly'] = weekly_ot
            data['holiday'] = holiday_ot
            return data
        
        

        def get_absence_policies(policy_group_id, day, data):

            if data == None or not data['_reuse']:
                data = {        
                        
                    'policy': None,
                    '_reuse': False,
                }
            elif data['_reuse']:
                return data

            absence_policy = self._get_absence_policy(policy_group_id, day)

            data['policy'] = absence_policy
            return data
        def get_presence_policies(policy_group_id, day, data):
    
                if data == None or not data['_reuse']:
                    data = {
                        'policy': None,
                        '_reuse': False,
                    }
                elif data['_reuse']:
                    return data
    
                policy = self._get_presence_policy(policy_group_id, day)
    
                data['policy'] = policy
                return data
    
        res = []
        for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context):
                  
            worked_hours_in_week = 0
            # Initialize list of leave's taken by the employee during the month
            leaves_list = self.leaves_list_init(
                cr, uid, contract.employee_id.id,
                day_from, day_to, contract.pps_id.tz, context=context)

            # Get default set of rest days for this employee/contract
            contract_rest_days = sched_tpl_obj.get_rest_days(cr, uid,
                                                             contract.schedule_template_id.id,
                                                             context=context)

            # Initialize dictionary of dates in this payslip and the hours the
            # employee was scheduled to work on each
            sched_hours_dict = sched_detail_obj.scheduled_begin_end_times_range(
                cr, uid,
                contract.employee_id.id,
                contract.id,
                day_from, day_to,
                context=context)

            # Initialize dictionary of hours worked per day
            working_hours_dict = self.attendance_dict_init(
                cr, uid, contract, day_from, day_to,
                context=None)

            # Short-circuit:
            # If the policy for the first day is the same as the one for the
            # last day assume that it will also be the same for the days in
            # between, and reuse the same policy instead of checking for every day.
            #
            ot_data = None
            data2 = None
            ot_data = get_ot_policies(
                contract.policy_group_id, day_from, ot_data)
            data2 = get_ot_policies(contract.policy_group_id, day_to, data2)
            if (ot_data['policy'] and data2['policy']) and ot_data['policy'].id == data2['policy'].id:
                ot_data['_reuse'] = True
            
            late_data = None     
            data2 = None
            late_data = get_late_policies(
                contract.policy_group_id, day_from, late_data)
            # data2 = get_late_policies(contract.policy_group_id, day_to, data2)
            if late_data['policy'] and late_data['policy'].id:
                late_data['_reuse'] = True
         
            absence_data = None
            data2 = None
            absence_data = get_absence_policies(
                contract.policy_group_id, day_from, absence_data)
            data2 = get_absence_policies(
                contract.policy_group_id, day_to, data2)
            if (absence_data['policy'] and data2['policy']) and absence_data['policy'].id == data2['policy'].id:
                absence_data['_reuse'] = True

            presence_data = None
            data2 = None
            presence_data = get_presence_policies(
                contract.policy_group_id, day_from, presence_data)
            data2 = get_presence_policies(
                contract.policy_group_id, day_to, data2)
            if (presence_data['policy'] and data2['policy']) and presence_data['policy'].id == data2['policy'].id:
                presence_data['_reuse'] = True

            # Calculate the number of days worked in the last week of
            # the previous month. Necessary to calculate Weekly Rest Day OT.
            #
            lsd = last_X_days()
            att_obj = self.pool.get('hr.attendance')
            att_ids = []
            if len(lsd.arr) == 0:
                d = day_from - timedelta(days=6)

                while d < day_from:
                    att_ids = att_obj.search(cr, uid, [
                        ('employee_id', '=', contract.employee_id.id),
                        ('name', '=', d.strftime(
                            '%Y-%m-%d')),
                    ],
                        order='name',
                        # XXX - necessary to keep
                        # order: in,out,in,out,...
                        context=context)
                    if len(att_ids) > 1:
                        lsd.push(True)
                    else:
                        lsd.push(False)
                    d += timedelta(days=1)

            attendances = {
                'MAX': {
                    'name': _("Maximum Possible Working Hours"),
                    'sequence': 1,
                    'code': 'MAX',
                    'number_of_days': 0.0,
                    'number_of_hours': 0.0,
                    'total_month_day':nb_of_days,
                    'contract_id': contract.id,
                },
            }
            leaves = {}
            att_obj = self.pool.get('hr.attendance')
            awol_code = False
            import logging
            _l = logging.getLogger(__name__)
            for day in range(0, nb_of_days):
                dtDateTime = datetime.strptime(
                    (day_from + timedelta(days=day)).strftime('%Y-%m-%d'), '%Y-%m-%d')
                rest_days = contract_rest_days
                normal_working_hours = 0

                # Get Presence data
                #
                presence_data = get_presence_policies(
                    contract.policy_group_id, dtDateTime.date(), presence_data)
                presence_policy = presence_data['policy']
                presence_codes = presence_policy and presence_obj.get_codes(
                    cr, uid, presence_policy.id, context=context) or []
                presence_sequence = 2

                for pcode, pname, ptype, prate, pduration in presence_codes:
                    if attendances.get(pcode, False):
                        continue
                    if ptype == 'normal':
                        normal_working_hours += float(pduration) / 60.0
                    attendances[pcode] = {
                        'name': pname,
                        'code': pcode,
                        'sequence': presence_sequence,
                        'number_of_days': 0.0,
                        'number_of_hours': 0.0,
                        'rate': prate,
                        'contract_id': contract.id,
                    }
                    presence_sequence += 1

                # Get OT data
                #
                ot_data = get_ot_policies(
                    contract.policy_group_id, dtDateTime.date(), ot_data)
                ot_policy = ot_data['policy']
                daily_ot = ot_data['daily']
                restday2_ot = ot_data['restday2']
                restday_ot = ot_data['restday']
                weekly_ot = ot_data['weekly']
                ot_codes = ot_policy and ot_obj.get_codes(
                    cr, uid, ot_policy.id, context=context) or []
                ot_sequence = 3

                for otcode, otname, ottype, otrate in ot_codes:
                    if attendances.get(otcode, False):
                        continue
                    attendances[otcode] = {
                        'name': otname,
                        'code': otcode,
                        'sequence': ot_sequence,
                        'number_of_days': 0.0,
                        'number_of_hours': 0.0,
                        'rate': otrate,
                        'contract_id': contract.id,
                    }
                    ot_sequence += 1
                
                # Get Late Data
                late_data = get_late_policies(contract.policy_group_id, dtDateTime, late_data)
                late_policy = late_data['policy']
                daily_late = late_data['daily']
                late_codes = late_policy and late_obj.get_codes(
                    cr, uid, late_policy.id, context=context) or []
                ot_sequence = 4
                
                for late_code in late_codes:
                    if attendances.get(late_code[0], False):
                        continue
                    latecode = late_code[0]
                    latename = late_code[1]
                    laterate = late_code[2]
                    attendances[latecode] = {
                        'name': latename,
                        'code': latecode,
                        'sequence': ot_sequence,
                        'number_of_days': 0.0,
                        'number_of_hours': 0.0,
                        'rate': laterate,
                        'contract_id': contract.id,
                    }
                    ot_sequence += 1
                
                # Get Absence data
                #
                absence_data = get_absence_policies(
                    contract.policy_group_id, dtDateTime.date(), absence_data)
                absence_policy = absence_data['policy']
                absence_codes = absence_policy and absence_obj.get_codes(
                    cr, uid, absence_policy.id, context=context) or []
                absence_sequence = 50

                for abcode, abname, abtype, abrate, useawol in absence_codes:
                    if leaves.get(abcode, False):
                        continue
                    if useawol:
                        awol_code = abcode
                    if abtype == 'unpaid':
                        abrate = 0
                    elif abtype == 'dock':
                        abrate = -abrate
                    leaves[abcode] = {
                        'name': abname,
                        'code': abcode,
                        'sequence': absence_sequence,
                        'number_of_days': 0.0,
                        'number_of_hours': 0.0,
                        'rate': abrate,
                        'contract_id': contract.id,
                    }
                    absence_sequence += 1

                # For Leave related computations:
                #    actual_rest_days: days that are rest days in schedule that was actualy used
                #    scheduled_hours: nominal number of full-time hours for the working day. If
                #                     the employee is scheduled for this day we use those hours. If
                #                     not we try to determine the hours he/she would have worked
                #                     based on the schedule template attached to the contract.
                #
                actual_rest_days = sched_obj.get_rest_days(
                    cr, uid, contract.employee_id.id,
                    dtDateTime, context=context)
                scheduled_hours = sched_detail_obj.scheduled_hours_on_day_from_range(
                    dtDateTime.date(),
                    sched_hours_dict)

                # If the calculated rest days and actual rest days differ, use
                # actual rest days
                if actual_rest_days != None and len(rest_days) != len(actual_rest_days):
                    rest_days = actual_rest_days
                elif actual_rest_days != None:
                    for d in actual_rest_days:
                        if d not in rest_days:
                            rest_days = actual_rest_days
                            break

                if scheduled_hours == 0 and dtDateTime.weekday() not in rest_days:
                    scheduled_hours = sched_tpl_obj.get_hours_by_weekday(
                        cr, uid, contract.schedule_template_id.id,
                        dtDateTime.weekday(
                        ),
                        context=context)

                # Actual number of hours worked on the day. Based on attendance
                # records.
                working_hours_on_day = self.attendance_dict_hours_on_day(
                    dtDateTime.date(), working_hours_dict)

                # Is today a holiday?
                public_holiday = self.holidays_list_contains(
                    dtDateTime.date(), public_holidays_list)

                # Keep count of the number of hours worked during the week for
                # weekly OT
                if dtDateTime.weekday() == contract.pps_id.ot_week_startday:
                    worked_hours_in_week = working_hours_on_day
                else:
                    worked_hours_in_week += working_hours_on_day

                push_lsd = True
                if working_hours_on_day:
                    done = False

                    if public_holiday:
                        _hours, push_lsd = self._book_holiday_hours(
                            cr, uid, contract, presence_policy, ot_policy, late_policy, attendances,
                            holiday_obj, dtDateTime, rest_days, lsd,
                            working_hours_on_day, context=context)
                        if _hours == 0:
                            done = True
                        else:
                            working_hours_on_day = _hours

                    if not done and restday2_ot:
                        _hours, push_lsd = self._book_restday_hours(
                            cr, uid, contract, presence_policy, ot_policy,
                            attendances, dtDateTime, rest_days, lsd,
                            working_hours_on_day, context=context)
                        if _hours == 0:
                            done = True
                        else:
                            working_hours_on_day = _hours

                    if not done and restday_ot:
                        _hours, push_lsd = self._book_weekly_restday_hours(
                            cr, uid, contract, presence_policy, ot_policy,
                            attendances, dtDateTime, rest_days, lsd,
                            working_hours_on_day, context=context)
                        if _hours == 0:
                            done = True
                        else:
                            working_hours_on_day = _hours

                    if not done and weekly_ot:
                        for line in ot_policy.line_ids:
                            if line.type == 'weekly' and (not line.weekly_working_days or line.weekly_working_days == 0):
                                _active_after = float(line.active_after) / 60.0
                                if worked_hours_in_week > _active_after:
                                    if worked_hours_in_week - _active_after > working_hours_on_day:
                                        attendances[line.code][
                                            'number_of_hours'] += working_hours_on_day
                                    else:
                                        attendances[line.code][
                                            'number_of_hours'] += worked_hours_in_week - _active_after
                                    attendances[line.code][
                                        'number_of_days'] += 1.0
                                    done = True

                    if not done and daily_ot:

                        # Do the OT between specified times (partial OT) first, so that it
                        # doesn't get double-counted in the regular OT.
                        #
                        partial_hr = 0
                        hours_after_ot = working_hours_on_day
                        for line in ot_policy.line_ids:
                            active_after_hrs = float(line.active_after) / 60.0
                            ot_day = line.ot_day 
                            working_hr = line.specific_work_hr
                            morning = line.morning 
                            cr.execute('SELECT EXTRACT(DOW FROM TIMESTAMP %s)',(dtDateTime,))
                            week_day=cr.fetchone()
                            week_day=int(week_day[0])                            
                            print 'OT Day' , ot_day
                            print 'working_hr------' , working_hr 
                            print 'Morning ------', morning                      
                            if line.type == 'daily' and ot_day:
                                print 'week_day ------', week_day                      
                                     
                                partial_hr = att_obj.partial_hours_on_day_by_specific_date_and_hours(
                                    cr, uid, contract,
                                    dtDateTime, active_after_hrs,
                                    line.active_start_time,
                                    line.active_end_time, morning, working_hours_on_day, ot_day, working_hr,
                                    line.tz, punches_list=self.attendance_dict_list(
                                        working_hours_dict),
                                    context=context)
                                print 'partial_hr',partial_hr
                                if partial_hr > 0:
                                    attendances[line.code][
                                        'number_of_hours'] += partial_hr
                                    attendances[line.code][
                                        'number_of_days'] += 1.0
                                    hours_after_ot -= partial_hr

                            
                            elif line.type == 'daily' and working_hours_on_day > active_after_hrs and line.active_start_time:
                                print 'Number of Days Shown on payslip For Shift is ============',attendances[line.code]['number_of_days']                                
                                partial_hr = att_obj.partial_hours_on_day(
                                    cr, uid, contract, dtDateTime, active_after_hrs,
                                    line.active_start_time, line.active_end_time, morning,
                                    line.tz, punches_list=self.attendance_dict_list(working_hours_dict),
                                    context=context)
                                if partial_hr > 0:
                                    attendances[line.code][
                                        'number_of_hours'] += partial_hr
                                    attendances[line.code][
                                        'number_of_days'] += 1.0
                                    hours_after_ot -= partial_hr
                        for line in ot_policy.line_ids:
                            active_after_hrs = float(line.active_after) / 60.0
                            print 'hours_after_ot',hours_after_ot
                            if line.type == 'daily' and hours_after_ot > active_after_hrs and not line.active_start_time:
                                attendances[line.code][
                                    'number_of_hours'] += hours_after_ot - (float(line.active_after) / 60.0)
                                attendances[line.code]['number_of_days'] += 1.0
                    
                    # late daily
                    print 'daily_late',daily_late
                    print 'late_policy',late_policy
                    if not done and daily_late and late_policy:

                        partial_hr = 0
    
                        print 'working_hours_on_day-------------' , working_hours_on_day
                        hours_after_late = working_hours_on_day
                        for line in late_policy.line_ids:
                            active_after_hrs = float(line.active_after) / 60.0
                            pay_day=line.pay_day
                            sat_late=line.sat_late
                            cr.execute('SELECT EXTRACT(DOW FROM TIMESTAMP %s)',(dtDateTime,))
                            week_day=cr.fetchone()
                            week_day=int(week_day[0])
                            
                            break_date=dtDateTime.date()
                            print'dtDateTime',break_date
                            print 'week_day',week_day
                            if line.type == 'daily' and pay_day and working_hours_on_day > active_after_hrs and line.active_start_time and week_day!=6 and sat_late ==False:

                                partial_hr = att_obj.late_hours_on_pay_day(cr, uid, contract,dtDateTime, active_after_hrs,line.active_start_time,line.active_end_time,pay_day,

                                    line.tz,

                                    punches_list=self.attendance_dict_list(

                                        working_hours_dict),

                                    context=context)

                             
                                if partial_hr > 0:

                                    attendances[line.code][

                                        'number_of_hours'] += partial_hr

                                    attendances[line.code][

                                        'number_of_days'] += 1.0

                                    hours_after_late -= partial_hr

                            elif line.type == 'daily' and working_hours_on_day > active_after_hrs and line.active_start_time and week_day!=6 and sat_late ==False:

                                partial_hr = att_obj.late_hours_on_day(
                                    cr, uid, contract,
                                    dtDateTime, active_after_hrs,
                                    line.active_start_time,
                                    line.active_end_time,
                                    line.tz,
                                    punches_list=self.attendance_dict_list(
                                        working_hours_dict),
                                    context=context)
                                if partial_hr > 0:
                                    attendances[line.code][
                                        'number_of_hours'] += partial_hr
                                    attendances[line.code][
                                        'number_of_days'] += 1.0
                                    hours_after_late -= partial_hr
                            elif line.type == 'daily' and pay_day and working_hours_on_day > active_after_hrs and line.active_start_time and week_day==6 and sat_late ==True:

                                partial_hr = att_obj.late_hours_on_pay_day(cr, uid, contract,dtDateTime, active_after_hrs,line.active_start_time,line.active_end_time,pay_day,

                                    line.tz,

                                    punches_list=self.attendance_dict_list(

                                        working_hours_dict),

                                    context=context)

                                                        
                                if partial_hr > 0:

                                    attendances[line.code][

                                        'number_of_hours'] += partial_hr

                                    attendances[line.code][

                                        'number_of_days'] += 1.0

                                    hours_after_late -= partial_hr

                            elif line.type == 'daily' and working_hours_on_day > active_after_hrs and line.active_start_time and week_day==6 and sat_late ==True:

                                partial_hr = att_obj.late_hours_on_day(
                                    cr, uid, contract,
                                    dtDateTime, active_after_hrs,
                                    line.active_start_time,
                                    line.active_end_time,
                                    line.tz,
                                    punches_list=self.attendance_dict_list(
                                        working_hours_dict),
                                    context=context)
                                if partial_hr > 0:
                                    attendances[line.code][
                                        'number_of_hours'] += partial_hr
                                    attendances[line.code][
                                        'number_of_days'] += 1.0
                                    hours_after_late -= partial_hr
                            elif line.type == 'break_over' and sat_late ==False:

                                cr.execute('''select count(att_time) from(
                                select (A.attendance-B.attendance)*60 as att_time from
                                                   ( select 
                                            (date_part('hour', cast(to_char(name::timestamp at time zone 'utc', 'yyyy-mm-dd hh24:mi:ss tz') as timestamp)) +
                                            (((date_part('minute', cast(to_char(name::timestamp at time zone 'utc', 'yyyy-mm-dd hh24:mi:ss tz') as timestamp)))/30)*0.5)) as attendance,att.name + '6 hour'::interval + '30 minutes'::interval as att_date,att.name::date as date
                                            from hr_attendance att 
                                            where  action='break_in'
                                            and att.name::date=%s
                                            and employee_id=%s
                                           
                                            )A,
                                
                                
                                                       (select 
                                            (date_part('hour', cast(to_char(name::timestamp at time zone 'utc', 'yyyy-mm-dd hh24:mi:ss tz') as timestamp)) +
                                            (((date_part('minute', cast(to_char(name::timestamp at time zone 'utc', 'yyyy-mm-dd hh24:mi:ss tz') as timestamp)))/30)*0.5)) as attendance,att.name + '6 hour'::interval + '30 minutes'::interval as att_date,att.name::date as date
                                            from hr_attendance att 
                                            where  action='break_out'
                                            and att.name::date=%s
                                            and employee_id=%s
                                            
                                            )B
                                where A.date=B.date
                                )C
                                where att_time>45''',(break_date,contract.employee_id.id,break_date,contract.employee_id.id))
                                partial_hr=cr.fetchone()
                                partial_hr=partial_hr[0]   
                                if partial_hr > 0:
                                    attendances[line.code][
                                        'number_of_hours'] += partial_hr
                                    attendances[line.code][
                                        'number_of_days'] += 1.0
                                    hours_after_late -= partial_hr 
                                    
                            elif line.type == 'break_absence' and sat_late ==False:
                                print 'break_date',contract.employee_id.id
                                cr.execute('''select coalesce(sum(count),0) as absent_count from
                                            (select count(AA.break_in_day) as count
                                                           from (
                                                        select  A.att_date::date as break_in_day,A.employee_id
                                                          from
                                                          (
                                                        select 
                                                        att.name + '6 hour'::interval + '30 minutes'::interval as att_date,att.employee_id
                                                        from hr_attendance att 
                                                        where action='break_out'
                                                        and att.name::date=%s
                                                        and employee_id=%s
                                                        )A
                                                        )AA
                                                        where AA.break_in_day not in
                                                        (
                                                        select att_date::date as in_date from(
                                                         select 
                                                        (date_part('hour', cast(to_char(name::timestamp at time zone 'utc', 'yyyy-mm-dd hh24:mi:ss tz') as timestamp)) +
                                                        (((date_part('minute', cast(to_char(name::timestamp at time zone 'utc', 'yyyy-mm-dd hh24:mi:ss tz') as timestamp)))/30)*0.5)) as attendance,att.name + '6 hour'::interval + '30 minutes'::interval as att_date 
                                                        from hr_attendance att 
                                                        where action='break_in'
                                                        and att.name::date=%s  
                                                        and employee_id=%s
                                                        
                                                        )A
                                                        )
                                                                    union all
                                                        select count(AA.break_out_day) as count
                                                           from (
                                                        select  A.att_date::date as break_out_day,A.employee_id
                                                          from
                                                          (
                                                        select 
                                                        att.name + '6 hour'::interval + '30 minutes'::interval as att_date,att.employee_id
                                                        from hr_attendance att 
                                                        where action='break_in'
                                                        and att.name::date=%s
                                                         and employee_id=%s

                                                        )A
                                                        )AA
                                                        where AA.break_out_day not in
                                                        (
                                                        select att_date::date as in_date from(
                                                         select 
                                                        (date_part('hour', cast(to_char(name::timestamp at time zone 'utc', 'yyyy-mm-dd hh24:mi:ss tz') as timestamp)) +
                                                        (((date_part('minute', cast(to_char(name::timestamp at time zone 'utc', 'yyyy-mm-dd hh24:mi:ss tz') as timestamp)))/30)*0.5)) as attendance,att.name + '6 hour'::interval + '30 minutes'::interval as att_date 
                                                        from hr_attendance att 
                                                        where action='break_out'
                                                        and att.name::date=%s
                                                        and employee_id=%s
                                                        
                                                        )A
                                                        )
                                            )B''',(break_date,contract.employee_id.id,break_date,contract.employee_id.id,break_date,contract.employee_id.id,break_date,contract.employee_id.id))
                                partial_hr=cr.fetchone()
                                partial_hr=partial_hr[0] 
                                print 'break absence',partial_hr  
                                if partial_hr > 0:
                                    attendances[line.code][
                                        'number_of_hours'] +=partial_hr
                                    attendances[line.code][
                                        'number_of_days'] += 1.0
                                    hours_after_late -= partial_hr 
                                              
                        for line in late_policy.line_ids:
                            active_after_hrs = float(line.active_after) / 60.0
                            if line.type == 'daily' and hours_after_late > active_after_hrs and not line.active_start_time and week_day!=6 and sat_late ==False:
                                attendances[line.code][
                                    'number_of_hours'] += hours_after_late - (float(line.active_after) / 60.0)
                                attendances[line.code]['number_of_days'] += 1.0
                            if line.type == 'daily' and hours_after_late > active_after_hrs and not line.active_start_time and week_day==6 and sat_late ==True:
                                attendances[line.code][
                                    'number_of_hours'] += hours_after_late - (float(line.active_after) / 60.0)
                                attendances[line.code]['number_of_days'] += 1.0
#                             if line.type == 'break_over' and sat_late ==False:
#                                 attendances[line.code][
#                                     'number_of_hours'] += hours_after_late - (float(line.active_after) / 60.0)
#                                 attendances[line.code]['number_of_days'] += 1.0   
#                             if line.type == 'break_absence' and sat_late ==False:
#                                 attendances[line.code][
#                                     'number_of_hours'] += hours_after_late - (float(line.active_after) / 60.0)
#                                 attendances[line.code]['number_of_days'] += 1.0                             
                    if not done and presence_policy:
                        for line in presence_policy.line_ids:
                            if line.type == 'normal':
                                normal_hours = self._get_applied_time(
                                    working_hours_on_day,
                                    line.active_after,
                                    line.duration)
                                attendances[line.code][
                                    'number_of_hours'] += normal_hours
                                attendances[line.code]['number_of_days'] += 1.0
                                done = True
                                _l.warning('nh: %s', normal_hours)
                                _l.warning('att: %s', attendances[line.code])

                    if push_lsd:
                        lsd.push(True)
                else:
                    lsd.push(False)

                leave_type, leave_hours = self.leaves_list_get_hours(
                    cr, uid, contract.employee_id.id,
                    contract.id, contract.schedule_template_id.id,
                    day_from + 
                    timedelta(
                        days=day),
                    leaves_list, context=context)
                if leave_type and (working_hours_on_day or scheduled_hours > 0 or dtDateTime.weekday() not in rest_days):
                    if leave_type in leaves:
                        leaves[leave_type]['number_of_days'] += 1.0
                        leaves[leave_type]['number_of_hours'] += (
                            leave_hours > scheduled_hours) and scheduled_hours or leave_hours
                    else:
                        leaves[leave_type] = {
                            'name': leave_type,
                            'sequence': 8,
                            'code': leave_type,
                            'number_of_days': 1.0,
                            'number_of_hours': (leave_hours > scheduled_hours) and scheduled_hours or leave_hours,
                            'contract_id': contract.id,
                        }
                elif awol_code and (scheduled_hours > 0 and working_hours_on_day < scheduled_hours) and not public_holiday:
                    hours_diff = scheduled_hours - working_hours_on_day
                    leaves[awol_code]['number_of_days'] += 1.0
                    leaves[awol_code]['number_of_hours'] += hours_diff

                # Calculate total possible working hours in the month
                if dtDateTime.weekday() not in rest_days:
                    attendances['MAX'][
                        'number_of_hours'] += normal_working_hours
                    attendances['MAX']['number_of_days'] += 1

            leaves = [value for key, value in leaves.items()]
            attendances = [value for key, value in attendances.items()]
            res += attendances + leaves 
        return res
    