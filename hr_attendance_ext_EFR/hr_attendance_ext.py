'''
Created on Sep 8, 2013

@author: phyo936
'''
from openerp.osv import fields, osv
from xlrd import open_workbook
import pytz
import logging
import base64
import pprint
from datetime import datetime

pp = pprint.PrettyPrinter(indent=4)
logger = logging.getLogger("Import Attendance")
class hr_fingerprint_device(osv.osv):
    _name = "hr.fingerprint.device"
    _description = "FingerPrint Device"
    _columns = {
              'name':fields.char('Fingerprint Device', size=64, required=True),
              'address':fields.char('URL'),
              'location':fields.char('Location'),
              'company_id': fields.many2one('res.company', 'Company', required=False),
              'active' : fields.boolean('Active', help="If the active field is set to False, it will allow you to hide the resource record without removing it."),
              }
    _defaults = {
        'active' : True,
    }
hr_fingerprint_device()

class hr_employee(osv.osv):
    _inherit = 'hr.employee'
    _columns = {
        'fingerprint_id': fields.char('ID', required=True),
        'identification_id':fields.char('NRC No', size=32),
        'father_name':fields.char('Father Name', size=45),
        'house_hold_file':fields.binary('House Hold Image'),
        'nrc_file':fields.binary('NRC Image'),
        'blood_group':fields.char('Blood Group'),
        
              }
    _sql_constraints = [('fingerprint_id_unique', 'unique(fingerprint_id)', 'Finger Employee ID must be unique')]
hr_employee()

class hr_contract(osv.osv):
    _inherit = 'hr.contract'
    _columns = {
                'joining_date':fields.char('Joining Date'),
    
                    }
hr_contract()

class hr_attendance(osv.osv):
    _inherit = 'hr.attendance'
    _columns = {
               
              'action': fields.selection(
                                             [('sign_in', 'Sign In'),
                                               ('break_out', 'Break Out'),
                                               ('break_in', 'Break In'),
                                              ('sign_out', 'Sign Out')],
                                             'Action', required=False),

                 }
    def _altern_si_so(self, cr, uid, ids):
        """ Implementing this logic at the attendance level doesn't work, so
        we skip it, and check at the whole time sheet level. 's all good!"""
        return True

    _constraints = [(_altern_si_so,
                     'Error: You should never see this message.',
                     ['action'])]
hr_attendance()   
    
class hr_fingerprint_attedance_file(osv.osv):
    _name = 'hr.fingerprint.attedance.file'
    _columns = {
        'name':fields.char('Description', required=True),
        'datas': fields.binary('File', required=True),
        'att_fname': fields.char('Filename', size=128, required=True),
        'fingerprint_device':fields.many2one('hr.fingerprint.device', 'Finger Print Device'),
        'upload_date': fields.date('Date Upload', readonly=True),
        'attendance_date':fields.date('Attendance From Date'),
        'attendance_date_to':fields.date('Attendance To Date'),
        'company_id':fields.many2one('res.company', 'Company')
          }
    
    _defaults = {
        # 'att_fname': '',
        'company_id':lambda self, cr, uid, context:uid,
        'upload_date':fields.date.context_today,
    }
    
    def att_create(self, cr, uid, ids, context=None):
        lines = []
        data = self.browse(cr, uid, ids)[0]

        file_name = data['att_fname']
        excel_file_import = False
        if file_name.find('.xls') != -1:
            excel_file_import = True
            excel_data = base64.decodestring(data['datas'])
            wb = open_workbook(file_contents=excel_data)
            for s in wb.sheets():
                # header
                headers = []
                header_row = 0
                for hcol in range(0, s.ncols):
                    headers.append(s.cell(header_row, hcol).value)
                # add header
                for row in range(header_row + 1, s.nrows):
                    values = []
                    for col in range(0, s.ncols):
                        values.append(s.cell(row, col).value)
                    lines.append(values)
        else:
            data_txt = base64.decodestring(data['datas'])
        # reader = csv.reader(StringIO.StringIO(lines), delimiter="    ")
            lines = data_txt.split('\n')
        ctx = {
                'attendance_date': data['attendance_date'],
                'attendance_date_to': data['attendance_date_to'],
                'company_id':data['company_id']            }
        self.create_att_new(cr, uid, lines, excel_file_import, context=ctx)
        # return super(hr_fingerprint_attedance_file, self).create(cr, uid, data, context=None)
####excel import    
    def _create_attendance_line(self, cr, uid, name, action, emp_id, company_id, context=None):
        attendance_pool = self.pool.get("hr.attendance")
        try:
            values = {'name': name, 'action': action, 'employee_id': emp_id, 'company_id':company_id.id}
            logger.info('Creating %s for %s on %s', action, emp_id, name)
            attendance_pool.create(cr, uid, values, context)
            cr.commit()
        except Exception, e:
            print e
            pass
        return True
####excel import
    def _check_attendance(self, cr, uid, emp_id, action_date, action, employee_code, company_id, context=None):
        attendance_pool = self.pool.get("hr.attendance")
        attendance_ids = attendance_pool.search(cr, uid, [('employee_id', '=', emp_id[0]), ('name', '=', action_date), ('action', '=', action)])
        if attendance_ids:
            
            logger.warn("Attendance '%s' is already entered for %s on %s", action, emp_id[0], action_date)
        else:
            self._create_attendance_line(cr, uid, action_date, action, emp_id[0], company_id)

        return True
# ##excel import
    def create_attendance_line(self, cr, uid, employee_id, entry_date, intime, outime, breakoutime , breakintime , employee_code, company_id, context=None):

        if intime :
            intime = datetime.strptime(intime, "%H:%M:%S").strftime("%H:%M:%S")
            self._check_attendance(cr, uid, employee_id, entry_date + ' ' + intime, 'sign_in', employee_code, company_id)
        if outime:
            outime = datetime.strptime(outime, "%H:%M:%S").strftime("%H:%M:%S")
            self._check_attendance(cr, uid, employee_id, entry_date + ' ' + outime, 'sign_out', employee_code, company_id)
        
        if breakoutime:
            breakoutime = datetime.strptime(breakoutime, "%H:%M:%S").strftime("%H:%M:%S")
            self._check_attendance(cr, uid, employee_id, entry_date + ' ' + breakoutime, 'break_out', employee_code, company_id)
        
        if breakintime :
            breakintime = datetime.strptime(breakintime, "%H:%M:%S").strftime("%H:%M:%S")
            self._check_attendance(cr, uid, employee_id, entry_date + ' ' + breakintime, 'break_in', employee_code, company_id)
        return True

    def close_attendance(self, cr, uid, last_attendance, date_close, context=None):
        attendance_pool = self.pool.get("hr.attendance")
        timesheet_sheet_pool = self.pool.get("hr_timesheet_sheet.sheet")
        logger.info('Closing Timesheet of the Employee with Open Sheet of the day.')
        for employee in last_attendance:
            sheet_ids = timesheet_sheet_pool.search(cr, uid, [('employee_id', 'in', employee), ('date_from', '<=', date_close), ('date_to', '>=', date_close)])
            if sheet_ids:
                status = timesheet_sheet_pool.read(cr, uid, sheet_ids[0], ['state_attendance'])['state_attendance']
                if status == 'present':
                    values = {'employee_id': employee,
                    'name': date_close + " 23:59:00",
                    'action': 'sign_out', } 
                    att_id = attendance_pool.create(cr, uid, values)
        logger.info("All timesheet has been closed for the respective singin entries for the day '%s'." % (date_close))
        return True
   
    def _input_tz(self, cr, uid, context):
        # if there's a tz in context, try to use that
        if context.get('tz'):
            try:
                return pytz.timezone(context['tz'])
            except pytz.UnknownTimeZoneError:
                pass

        # if the current user has a tz set, try to use that
        user = self.pool['res.users'].read(
            cr, uid, [uid], ['tz'], context=context)[0]
        if user['tz']:
            try:
                return pytz.timezone(user['tz'])
            except pytz.UnknownTimeZoneError:
                pass

        # fallback if no tz in context or on user: UTC
        return pytz.UTC
# ##two time condition for one line two action (sign_in ,sign_out)Excel
    def prepared_attendance_excel(self, fields, input_tz, attendances):
        if len(fields) < 29:
            return;
# ##need to fix date time format for EFR        
        
        emp_id = int(fields[0])
        emp_name = fields[3]
        date_data = str(fields[5])
        time_in = fields[9]
        time_out = fields[10]
        if time_in:
            t_in = time_in + ':00'
            in_time = date_data + ' ' + t_in
            date_time_in = datetime.strptime(in_time, '%m/%d/%Y %H:%M:%S')
        if time_out:    
            t_out = time_out + ':00'
            out_time = date_data + ' ' + t_out
            date_time_out = datetime.strptime(out_time, '%m/%d/%Y %H:%M:%S')
        if time_in:
            local_date_entry = date_time_in
            dt = input_tz.localize(local_date_entry, is_dst=False)
        # And convert to UTC before reformatting for writing
            utc_date_entry = dt.astimezone(pytz.UTC)
            # utc_date_entry_str = dt.astimezone(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S')
            # there two type of timezone 1.utc_date_entry and 2.utc_date_entry_str
            date_only = utc_date_entry.strftime("%Y-%m-%d")
            time_entry = utc_date_entry.strftime("%H:%M:%S")
            action_desc = 'inTime'
            
            vals = {}
            vals['id'] = emp_id
            vals['Name'] = emp_name
            vals['action'] = 'inTime'
            vals['aDate'] = date_only
            vals[action_desc] = time_entry
            vals['date'] = date_only
            
            
            in_exist = False
            for att in attendances:
                if int(att['id']) == emp_id and att['date'] == date_only and att['action'] != action_desc:
                    att[action_desc] = time_entry
                    in_exist = True;
                    break;     
            if not in_exist:
                    attendances.append(vals)
                
        if time_out:
            # out time for new entry
            local_date_entry_out = date_time_out
            dt_out = input_tz.localize(local_date_entry_out, is_dst=False)
        # And convert to UTC before reformatting for writing
            utc_date__out_entry = dt_out.astimezone(pytz.UTC)
            # utc_date_entry_out_str = dt_out.astimezone(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S')
            # there two type of timezone 1.utc_date_entry and 2.utc_date_entry_str
            date_out_only = utc_date__out_entry.strftime("%Y-%m-%d")
            time_entry_out = utc_date__out_entry.strftime("%H:%M:%S")
            action_desc = 'outTime'
            
            out_vals = {}
            out_vals['id'] = emp_id
            out_vals['Name'] = emp_name
            out_vals['action'] = action_desc
            out_vals['aDate'] = date_out_only
            out_vals[action_desc] = time_entry_out
            out_vals['date'] = date_only
            in_exist = False
            for att in attendances:
                if int(att['id']) == emp_id and att['date'] == date_only and att['action'] != action_desc:
                    att[action_desc] = time_entry_out
                    in_exist = True;
                    break;       
            if not in_exist:
                    attendances.append(out_vals)
            
    # #dat import    
    def prepared_name_attendance(self, fields, input_tz, attendances):
        action_desc = "";
        local_date_entry = datetime.strptime(fields[2], '%Y-%m-%d %H:%M:%S')
        dt = input_tz.localize(local_date_entry, is_dst=False)
    # And convert to UTC before reformatting for writing
        utc_date_entry = dt.astimezone(pytz.UTC)
        utc_date_entry_str = dt.astimezone(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S')
        date_only = utc_date_entry.strftime("%Y-%m-%d")
        time_entry = utc_date_entry.strftime("%H:%M:%S")
        vals = {}
        
        if(int(fields[4]) == 1):
            action_desc = 'outTime'
            vals[action_desc] = utc_date_entry
        elif(int(fields[4]) == 2):
            action_desc = 'Breakout'
            vals[action_desc] = utc_date_entry
        elif(int(fields[4]) == 3):
            action_desc = 'Breakin'
            vals[action_desc] = utc_date_entry
        elif(int(fields[4]) == 0):
            action_desc = 'inTime'
            vals[action_desc] = utc_date_entry
            
        emp_id = int(fields[0])
        exist = False
        for att in attendances:
            if int(att['id']) == int(emp_id) and att['date'] == date_only:
                exist = True
            if int(att['id']) == emp_id and att['date'] == date_only and att['action'] != action_desc:
                att[action_desc] = time_entry
        
        vals['id'] = int(fields[0])
        vals['Name'] = fields[1]
        vals['action'] = action_desc
        vals['aDate'] = utc_date_entry_str
        vals[action_desc] = time_entry
        vals['date'] = date_only
        if not exist:
                attendances.append(vals)
                
    def prepared_wihtoutname_attendance(self, fields, input_tz, attendances):
        action_desc = "";
        local_date_entry = datetime.strptime(fields[1], '%Y-%m-%d %H:%M:%S')
        dt = input_tz.localize(local_date_entry, is_dst=False)
    # And convert to UTC before reformatting for writing
        utc_date_entry = dt.astimezone(pytz.UTC)
        utc_date_entry_str = dt.astimezone(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S')
        date_only = utc_date_entry.strftime("%Y-%m-%d")
        time_entry = utc_date_entry.strftime("%H:%M:%S")
        vals = {}
            
        if(int(fields[3]) == 1):
            action_desc = 'outTime'
            vals[action_desc] = utc_date_entry
        elif(int(fields[3]) == 2):
            action_desc = 'Breakout'
            vals[action_desc] = utc_date_entry
        elif(int(fields[3]) == 3):
            action_desc = 'Breakin'
            vals[action_desc] = utc_date_entry
        elif(int(fields[3]) == 0):
            action_desc = 'inTime'
            vals[action_desc] = utc_date_entry
            
        emp_id = int(fields[0])
        # emp_name = fields[1];  
        exist = False
        for att in attendances:
            if int(att['id']) == emp_id and att['date'] == date_only:
                exist = True
            if int(att['id']) == emp_id and att['date'] == date_only and att['action'] != action_desc:
                att[action_desc] = time_entry
        
        vals['id'] = int(fields[0])
        vals['action'] = action_desc
        vals['aDate'] = utc_date_entry_str
        vals[action_desc] = time_entry
        vals['date'] = date_only
        if not exist:
                attendances.append(vals)
    # Excel           
    def prepared_attendance(self, cr, uid, lines, excel_import_file, context=None):
        attendances = []
        input_tz = self._input_tz(cr, uid, context)  # Apply input tz to the parsed naive datetime
        for line in lines:
            if excel_import_file and line:
                self.prepared_attendance_excel(line, input_tz, attendances)
            else:
                fields = line.split('\t')
                if len(fields) == 5:
                    self.prepared_name_attendance(fields, input_tz, attendances)
                elif len(fields) == 6: 
                    self.prepared_wihtoutname_attendance(fields, input_tz, attendances)
        return attendances
####excel function call from xml file
    def create_attendance_new(self, cr, uid, lines, context=None):
        employee_pool = self.pool.get("hr.employee")
        emp_fingerprint = {}
        emp_ids = employee_pool.search(cr, uid, [])
        hr_emp_data = employee_pool.read(cr, uid, emp_ids, ['id', 'fingerprint_id'])
        
        for emp in hr_emp_data:
            if emp['fingerprint_id']:
                emp_fingerprint[int(emp['fingerprint_id'])] = emp['id']  
        attendances = self.prepared_attendance(cr, uid, lines, context)
        print "Total Number of attendance records %d" % len(attendances)
        invalid_ids = []
        for attance_line in attendances:
            try:
                entry_date = attance_line['date']
                # print str(attance_line['id']).split()
                cr.execute("select name_related from hr_employee where fingerprint_id  = %s", (str(attance_line['id']).split()))
                employee_code = cr.fetchone()
                if employee_code is None and invalid_ids.count(attance_line['id']) == 0:
                    invalid_ids.append(attance_line['id'])
                else:
                    if 'Name' in attance_line:
                        employee_code = attance_line['Name']
                        # e_id = employee_pool.search(cr,uid,[('fingerprint_id','=',attance_line['id'])])
                        if not attance_line['id'] in emp_fingerprint :
                            employee_ids = [employee_pool.create(cr, uid, {'name': employee_code, 'fingerprint_id':attance_line['id']})]
                            employee_id = employee_ids[0]
                            emp_fingerprint[attance_line['id']] = employee_id
                    elif int(attance_line['id']) in emp_fingerprint:
                        employee_id = emp_fingerprint[int(attance_line['id'])]

                    in_time = None
                    out_time = None
                    break_in_time = None
                    break_out_time = None
                    if 'inTime' in attance_line:
                        in_time = attance_line['inTime']
                    if 'outTime' in attance_line:
                        out_time = attance_line['outTime']
                    if 'Breakout' in attance_line:
                        break_out_time = attance_line['Breakout']
                    if 'Breakin' in attance_line:
                        break_in_time = attance_line['Breakin']
                    print 'in time', in_time
                    print 'out time', out_time    
                    if employee_code and employee_id and entry_date:
                        self.create_attendance_line(cr, uid, employee_id, entry_date, in_time, out_time, break_out_time , break_in_time, employee_id)
            except Exception, e:
                logger.error('Error %s', e)
        if len(invalid_ids) > 0:
            raise osv.except_osv(('Invalid Id[s]!'), ('User Id[s]: %s are not register as users!!' % (invalid_ids)))
        logger.info("Import Attendance Completed.")
        return True
    
    
    # Created by Thiha (11-Dec-2013) EXCEL (EFR)
    def create_att_new(self, cr, uid, lines, excel_import_file, context):
        employee_pool = self.pool.get("hr.employee")
        emp_fingerprint = {}
        emp_ids = employee_pool.search(cr, uid, [])
        hr_emp_data = employee_pool.read(cr, uid, emp_ids, ['id', 'fingerprint_id'])
        from_date = context['attendance_date']
        to_date = context['attendance_date_to']
        company_id = context['company_id']
        for emp in hr_emp_data:
            if emp['fingerprint_id']:
                emp_fingerprint[int(emp['fingerprint_id'])] = emp['id']  
        attendances = self.prepared_attendance(cr, uid, lines, excel_import_file, context)
        print "Total Number of attendance records %d" % len(attendances)
        invalid_ids = []
        name_exist = False;
        for attance_line in attendances:
            try:
                entry_date = attance_line['date']
                cr.execute("select name_related from hr_employee where fingerprint_id  = %s", (str(attance_line['id']).split()))
                employee_code = cr.fetchone()
                
                if employee_code is None and invalid_ids.count(attance_line['id']) == 0:
                    invalid_ids.append(attance_line['id'])
                    
                if 'Name' in attance_line:
                    employee_code = attance_line['Name']
                    cr.execute("select name_related from hr_employee where fingerprint_id  = %s", (str(attance_line['id']).split()))
                    emp_name = cr.fetchone()
                    name_exist = True
                    if emp_name is None:
                        employee_ids = [employee_pool.create(cr, uid, {'name': employee_code, 'fingerprint_id':attance_line['id'], 'company_id':company_id.id})]
                        employee_id = employee_ids[0]
                        emp_fingerprint[attance_line['id']] = employee_id
                    else:
                        cr.execute("select id from hr_employee where fingerprint_id = %s", (str(attance_line['id']).split()))
                        employee_id = cr.fetchone()
                        
                elif int(attance_line['id']) in emp_fingerprint:
                    employee_id = emp_fingerprint[int(attance_line['id'])]
                    
                in_time = None
                out_time = None
                break_in_time = None
                break_out_time = None
                if 'inTime' in attance_line:
                    in_time = attance_line['inTime']
                    
                if 'outTime' in attance_line:
                    out_time = attance_line['outTime']
               
                if 'Breakout' in attance_line:
                    break_out_time = attance_line['Breakout']
                    
                if 'Breakin' in attance_line:
                    break_in_time = attance_line['Breakin']
                if employee_code and employee_id and from_date <= entry_date <= to_date :
                    self.create_attendance_line(cr, uid, employee_id, entry_date, in_time, out_time , break_out_time , break_in_time , employee_code, company_id)
                    
            except Exception, e:
                logger.error('Error %s', e)
                
        if len(invalid_ids) > 0 and name_exist == False:
            raise osv.except_osv(('Invalid Id[s]!'), ('User Id[s]: %s are not register as users!!' % (invalid_ids)))
        logger.info("Import Attendance Completed.")
        
        return True
    
hr_fingerprint_attedance_file() 
