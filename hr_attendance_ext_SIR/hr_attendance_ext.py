'''
Created on Sep 8, 2013

@author: phyo936
'''
from openerp.osv import orm
from openerp.osv import fields, osv
from openerp.tools.translate import _
import base64, StringIO, csv
from openerp.osv import orm
from openerp.osv import fields, osv
from content_index import cntIndex
from xlrd import open_workbook
import base64
import logging
import time
import psycopg2
import base64, StringIO, csv
import pytz
from openerp.tools.misc import ustr
from dateutil.relativedelta import relativedelta
import pprint
from datetime import datetime
#from matplotlib.dates import date2num,num2date
import xlrd
_logger = logging.getLogger(__name__)


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
        'street1':fields.char('Street'),
        'township':fields.char('Township'),
        
              }
    _sql_constraints = [('fingerprint_id_unique', 'unique(fingerprint_id)', 'Finger Employee ID must be unique')]
hr_employee()

class hr_contract(osv.osv):
    _inherit = 'hr.contract'
    _columns = {
                'joining_date':fields.char('Joining Date'),
    
                    }

class hr_attendance(osv.osv):
    _inherit = 'hr.attendance'
    _columns = {
               'company_id':fields.many2one('res.company', 'Company'),

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
    
    _defaults = {
               'company_id':lambda self, cr, uid, context:uid,
               }

    _constraints = [(_altern_si_so, 
                     'Error: You should never see this message.', 
                     ['action'])]
hr_attendance()   
    
class hr_fingerprint_attedance_file(osv.osv):
    _name = 'hr.fingerprint.attedance.file'
    _columns = {
        'name':fields.char('Description',required=True), 
        'datas': fields.binary('File', required=True),
        'att_fname': fields.char('Filename', size=128, required=True),       
        'fingerprint_device':fields.many2one('hr.fingerprint.device', 'Finger Print Device'),
        'upload_date': fields.date('Date Upload', readonly=True),
        'attendance_date':fields.date('Attendance From Date'),
        'attendance_date_to':fields.date('Attendance To Date'),
         'company_id':fields.many2one('res.company','Company')
          }
    
    _defaults = {
        #'att_fname': '',
        'upload_date':fields.date.context_today,
    }
    
    def att_create(self, cr, uid,ids,input_tz,  context=None):
        lines=[]
        values=[]
        c=''
        header_fields = ['Name','sDate','Machine','Ac-No','sTime']
        data = self.browse(cr,uid,ids)[0]
        company_id = data.company_id.id
        file_name = data['att_fname']
        excel_file_import = False
        g=[]
        amls = []
        csv_file_import = False
        if file_name.find('.csv') !=-1:
            err_log = ''
            header_line = False 
            hr_employee_obj = self.pool.get('hr.employee')
            hr_att_obj = self.pool.get('hr.attendance')
            csv_file_import = True
            csv_data = base64.decodestring(data['datas'])
            r=csv.reader(StringIO.StringIO(csv_data), delimiter=",")
            print 'r',r
            
            for ln in r:
                if not ln or ln and ln[0] and ln[0][0] in ['', '#']:
                    continue
                
                # process header line
                if not header_line:
                    if ln[0].strip() not in header_fields:
                        raise orm.except_orm(_('Error :'), _("Error while processing the header line %s. \n\nPlease check your CSV separator as well as the column header fields") %ln)
                    else:
                        header_line = True
                        Name_i = sDate_i = Machine_i = Ac_No_i = sTime_i = None
                        column_cnt = 0
                        for cnt in range(len(ln)):
                            if ln[cnt] == '':
                                column_cnt = cnt
                                break
                            elif cnt == len(ln)-1:
                                column_cnt = cnt + 1
                                break
                        for i in range(column_cnt):
                            # header fields
                            header_field = ln[i].strip()
                            if header_field not in header_fields:
                                err_log += '\n' + _("Invalid CSV File, Header Field '%s' is not supported !") %ln[i]
                            # required header fields : account, debit, credit
                            elif header_field == 'Name':
                                Name_i = i
                            elif header_field == 'sDate':
                                sDate_i = i
                            elif header_field == 'Machine':
                                Machine_i = i
                            elif header_field == 'Ac-No':
                                Ac_No_i = i
                            elif header_field == 'sTime':
                                sTime_i = i
                        for f in [(Name_i,'Name'),(sDate_i,'sDate'),(Machine_i,'Machine'),(Ac_No_i,'Ac-No'),(sTime_i,'sTime')]:
                            if not isinstance(f[0],int):
                                err_log += '\n'+ _("Invalid CSV file, Header '%s' is missing !") % f[1]
                            
                    #process data lines   
                else:
                    if ln and ln[0] and ln[0][0] not in ['#','']:
                        
                        import_vals = {}
                        print' Name',ln[Name_i]
                        import_vals['Name'] =  ln[Name_i]
                        import_vals['sDate'] = ln[sDate_i]
                        import_vals['Ac-No']= ln[Ac_No_i]
                        import_vals['Machine'] = ln[Machine_i]
                        import_vals['sTime'] = ln[sTime_i]
                        amls.append(import_vals)
                        
                        

#             reader=csv_data.split('\n')
#             print 'this is csv decoded',reader
#             for l in reader:
#                 line=l.replace(",","\t")
#                 lines.append(line)
#             print 'lines',lines
        elif file_name.find('.xls') !=-1:
            excel_file_import = True
            excel_data = base64.decodestring(data['datas'])
            wb = open_workbook(file_contents = excel_data)
            for s in wb.sheets():
                #header
                headers=[]
                header_row=0
                for hcol in range(0,s.ncols):
                    headers.append(s.cell(header_row,hcol).value)
                #add header
                for row in range(header_row+1,s.nrows):
                    values = []
                    for col in range(0,s.ncols):
                        values.append(s.cell(row,col).value)
                    lines.append(values)
                print 'lines',lines
        else:
            data_txt = base64.decodestring(data['datas'])
        #reader = csv.reader(StringIO.StringIO(lines), delimiter="    ")
            lines =data_txt.split('\n')
            print 'lines',lines
        ctx = {
                'attendance_date': data['attendance_date'],
                'attendance_date_to': data['attendance_date_to'],
                 'company_id':data['company_id']       
     }
#         if csv_file_import==True:
#             self.create_attendance_new_csv(cr, uid,lines,context=ctx)       
        if csv_file_import ==True:
            print 'csv aml',amls
            self.create_attendance_new_csv(cr,uid,amls,context=ctx)
   

        if excel_file_import==True:
            self.create_att_new(cr, uid, lines, excel_file_import,context=ctx)
        else:
            print 'line ',lines
            self.create_attendance_new(cr, uid, lines,context=ctx)
        return True
        #return super(hr_fingerprint_attedance_file, self).create(cr, uid, data, context=None)
    def create_att_csv(self,cr,uid,amls,company_id,context=None):
        input_tz = self._input_tz(cr, uid, context)
        hr_att_obj = self.pool.get('hr.attendance')
        hr_employee_obj = self.pool.get('hr.employee')
        for aml in amls:
            print 'aml',len(aml)
            att_id = emp_id = time_in = time_out = time_date = None
            emp_name = aml['Name']
            id = aml['Ac-No']
            time  = aml['sTime']

                    
                                        
            if emp_name :
                emp_id = hr_employee_obj.search(cr,uid,[('name','=',emp_name),('fingerprint_id','=',id)])
                if not emp_id:
                    emp_value = {'fingerprint_id':id,'name':emp_name}
                    emp_ids = hr_employee_obj.create(cr,uid,emp_value,context=context)
                else:
                    emp_ids = emp_id[0]
            if emp_ids :
                att_id =hr_att_obj.search(cr,uid,[('employee_id','=',emp_ids)])
                if not att_id:
                    print 'hellosssss'
            if time:
                if time.find('AM') !=-1:
                    print 'time',time
                    time_date = datetime.strptime(time,'%m/%d/%Y %H:%M:%S AM')
                    date_only = time_date.strftime("%m/%d/%Y")
                    year = time_date.strftime("%Y")
                    month = time_date.strftime("%m")
                    day = time_date.strftime("%d")
                    date = year+'-'+month+'-'+day
                    print 'date ',date 
                    time_entry = time_date.strftime("%H:%M:%S")
                    time_in = date+' '+time_entry
                    print 'time in ',time_in
                    if time_in:
                        att_id = hr_att_obj.search(cr,uid,['&',('employee_id','=',emp_ids),('name','=',time),('action','=','sign_in')])
                        if not att_id:
                            att_value = {'employee_id':emp_ids,'name':time,'action':'sign_in','company_id':company_id}
                            att_ids = hr_att_obj.create(cr,uid,att_value,context=context)
                        else:
                            att_ids =att_id[0]
                elif time.find('PM') !=-1:
                    print 'time',time
                    time_date = datetime.strptime(time,'%m/%d/%Y %H:%M:%S PM')
                    date_only = time_date.strftime("%m/%d/%Y")
                    year = time_date.strftime("%Y")
                    month = time_date.strftime("%m")
                    day = time_date.strftime("%d")
                    date = year+'-'+month+'-'+day
                    time_entry = time_date.strftime("%H:%M:%S")
                    time_out = date+' '+time_entry
                    print 'time in ',time_out
                    if time_out:
                        att_id = hr_att_obj.search(cr,uid,['&',('employee_id','=',emp_ids),('name','=',time),('action','=','sign_out')])
                        if not att_id:
                            att_value = {'employee_id':emp_ids,'name':time,'action':'sign_out','company_id':company_id}
                            att_ids = hr_att_obj.create(cr,uid,att_value,context=context)
                        else:
                            att_ids =att_id[0]
                print 'employee_id',emp_ids,' employee name',emp_name,' and  time',time
        return True
    def create_attendance_new_csv(self, cr, uid, values, context): 
        attendances = self.prepared_attendance_csv(cr, uid, values, context)
        return True
        
        return True
    def create_attendance_new(self, cr, uid, lines, context):
        employee_pool = self.pool.get("hr.employee")
        emp_fingerprint = {}
        emp_ids = employee_pool.search(cr, uid, [])
        hr_emp_data = employee_pool.read(cr, uid, emp_ids, ['id', 'fingerprint_id'])
        from_date  = context['attendance_date']
        to_date = context['attendance_date_to']
        for emp in hr_emp_data:
            if emp['fingerprint_id']:
                emp_fingerprint[int(emp['fingerprint_id'])] = emp['id']  
        attendances = self.prepared_attendance_dat(cr, uid, lines, context)
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
                        employee_ids = [employee_pool.create(cr, uid, {'name': employee_code, 'fingerprint_id':attance_line['id']})]
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
                
                if employee_code and employee_id and from_date<=entry_date<=to_date :
                    self.create_attendance_line(cr, uid, employee_id, entry_date, in_time, out_time , break_out_time ,break_in_time , employee_code)
                    
            except Exception, e:
                logger.error('Error %s', e)
                
        if len(invalid_ids) > 0 and name_exist == False:
            raise osv.except_osv(('Invalid Id[s]!'), ('User Id[s]: %s are not register as users!!' % (invalid_ids)))
        logger.info("Import Attendance Completed.")
        
        return True
    
    def _create_attendance_line(self, cr, uid, name, action, emp_id, code,company_id, context=None):
        attendance_pool = self.pool.get("hr.attendance")
        values = {}
        try:
            values = {'name': name, 'action': action, 'employee_id': emp_id,'company_id':company_id}
            print 'values is .....',values
            logger.info('Creating %s for %s on %s', action, code, name)
            attendance_pool.create(cr, uid, values, context)
            cr.commit()
        except Exception, e:
            print e,"Error creating attendance",values
            pass
        return True

    def _check_attendance(self, cr, uid, emp_id, action_date, action, employee_code,company_id, context=None):
        attendance_pool = self.pool.get("hr.attendance")
        attendance_ids = attendance_pool.search(cr, uid, [('employee_id', '=', emp_id), ('name', '=', action_date), ('action', '=', action)])
        if attendance_ids:
            logger.warn("Attendance '%s' is already entered for %s on %s", action, employee_code, action_date)
        else:
            self._create_attendance_line(cr, uid, action_date, action, emp_id, employee_code,company_id)
        return True

    def create_attendance_line(self, cr, uid, employee_id, entry_date, intime, outime, breakoutime , breakintime , employee_code,  company_id):
        attendance_pool = self.pool.get("hr.attendance")
      #  timesheet_sheet_pool = self.pool.get("hr_timesheet_sheet.sheet")
       # sheet_ids = timesheet_sheet_pool.search(cr, uid, [('employee_id', '=', employee_id), ('date_from', '<=', entry_date), ('date_to', '>=', entry_date)])
        #if not sheet_ids:
         #   date_to = (datetime.strptime(entry_date, '%Y-%m-%d') + relativedelta(weekday=6)).strftime('%Y-%m-%d')
          #  date_from = (datetime.strptime(entry_date, '%Y-%m-%d') + relativedelta(weekday=0, days=-6)).strftime('%Y-%m-%d')
           # sheet_ids = [timesheet_sheet_pool.create(cr, uid, {'employee_id':employee_id, 'date_from':date_from, 'date_to':date_to, 'date_current': entry_date})]
        # Todo: Each time it goes for search.For If Same entry is doen or Not.
        if intime :
            intime = datetime.strptime(intime, "%H:%M:%S").strftime("%H:%M:%S")
            self._check_attendance(cr, uid, employee_id, entry_date + ' ' + intime, 'sign_in', employee_code,company_id)
       # else:
        #    self._check_attendance(cr, uid, employee_id, entry_date + ' 01:00:00', 'sign_in', employee_code)
        if outime:
            outime = datetime.strptime(outime, "%H:%M:%S").strftime("%H:%M:%S")
            self._check_attendance(cr, uid, employee_id, entry_date + ' ' + outime, 'sign_out', employee_code,company_id)
        if not outime:
            outime = datetime.strptime(outime, "%H:%M:%S").strftime("%H:%M:%S")
            self._check_attendance(cr, uid, employee_id, entry_date + ' ' + outime, 'sign_out', employee_code,company_id)
        
        if breakoutime:
            breakoutime = datetime.strptime(breakoutime, "%H:%M:%S").strftime("%H:%M:%S")
            self._check_attendance(cr, uid, employee_id, entry_date + ' ' + breakoutime, 'break_out', employee_code,company_id)
        
        if breakintime :
            breakintime = datetime.strptime(breakintime, "%H:%M:%S").strftime("%H:%M:%S")
            self._check_attendance(cr, uid, employee_id, entry_date + ' ' + breakintime, 'break_in', employee_code,company_id)
       # else:
        #    self._check_attendance(cr, uid, employee_id, entry_date + ' 01:00:00', 'sign_in', employee_code)
        
        #else:
         #   self._check_attendance(cr, uid, employee_id, entry_date + ' 23:00:00', 'sign_out', employee_code)
        return True

    def close_attendance(self, cr, uid, last_attendance, date_close, context=None):
        attendance_pool = self.pool.get("hr.attendance")
        timesheet_sheet_pool = self.pool.get("hr_timesheet_sheet.sheet")
        logger.info('Closing Timesheet of the Employee with Open Sheet of the day.')
        for employee in last_attendance:
            sheet_ids = timesheet_sheet_pool.search(cr, uid, [('employee_id', '=', employee), ('date_from', '<=', date_close), ('date_to', '>=', date_close)])
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
    def prepared_attendance_excel(self,fields,input_tz,attendances):
        print 'fields',fields
        if len(fields)>29:
            return;
        time_in=time_out=False
        in_day = fields[3]
        emp_id = int(fields[2])
        emp_name=fields[1]
        ###Excel for Fixed or Changes
        try:
            data_time = float(fields[3])
            result= xlrd.xldate.xldate_as_tuple(data_time,0)
            timestamp = fields[3]
            a= str(result[1])+'/'+str(result[2])+'/'+str(result[0])+' '+str(result[3])+':'+str(result[4])+':'+str(result[5])
    
            date_data = str(datetime.strptime(a, '%m/%d/%Y %H:%M:%S'))
            time = fields[4]
            print in_day
            print date_data
            print time
            if time.find('In') !=-1:
                date_time_in = date_data
                time_in = True
                print 'in time',date_time_in
                local_date_entry = None
                try:
                    local_date_entry = datetime.strptime(date_time_in, '%d-%b-%y %H:%M:%S')
                except Exception, e:
                    if date_time_in:
                        local_date_entry = datetime.strptime(date_time_in, '%Y-%m-%d %H:%M:%S') 
                        dt = input_tz.localize(local_date_entry, is_dst=False)
                    # And convert to UTC before reformatting for writing
                        utc_date_entry=dt.astimezone(pytz.UTC)
                        utc_date_entry_str = dt.astimezone(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S')
                        print utc_date_entry_str
                        date_only = utc_date_entry.strftime("%Y-%m-%d")
                        time_entry = utc_date_entry.strftime("%H:%M:%S")
                        action_desc = 'inTime'
                        vals={}
                        vals['id'] = emp_id
                        vals['Name'] = emp_name
                        vals['action'] = 'inTime'
                        vals['aDate'] = utc_date_entry_str
                        vals['inTime'] = time_entry
                        vals['date'] = date_only
                        vals['in_day'] = in_day
                        in_exist = False
                        for att in attendances:
                            if int(att['id']) == emp_id and att['date'] == date_only and att['action'] != action_desc:
                                att[action_desc] = time_entry
                                in_exist = True;
                                break;
                                
                        if not in_exist:
                                attendances.append(vals)
                                print 'this is in time',time
                                return attendances
            if time.find('Out') !=-1:
                date_time_out = date_data
                print 'out time',date_time_out
                time_out = True
                local_date_entry_out = None
                try:
                    local_date_entry_out = datetime.strptime(date_time_out, '%d-%b-%y:%M:%S')
                except Exception, e:
                    print e,date_time_out
                    if date_time_out:
                        local_date_entry_out = datetime.strptime(date_time_out, '%Y-%m-%d %H:%M:%S') 
                        dt_out = input_tz.localize(local_date_entry_out, is_dst=False)
                    # And convert to UTC before reformatting for writing
            #             utc_date_entry=dt_out.astimezone(pytz.UTC)
                        utc_date__out_entry=dt_out.astimezone(pytz.UTC)
                        utc_date_entry_out_str = dt_out.astimezone(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S')
                        date_only = utc_date__out_entry.strftime("%Y-%m-%d")
            
                        date_out_only = utc_date__out_entry.strftime("%m/%d/%Y")
                        time_entry_out = utc_date__out_entry.strftime("%H:%M:%S")
                        action_desc = 'outTime'
                        out_vals={}
                        out_vals['id'] = emp_id
                        out_vals['Name'] = emp_name
                        out_vals['action'] = action_desc
                        out_vals['aDate'] = utc_date_entry_out_str
                        out_vals['outTime'] = time_entry_out##that my fix
                        out_vals['date'] = date_only
                        out_vals['in_day'] = in_day
                        attendances.append(out_vals)
                        return attendances 
        ####Excel Not Changes or Fix
        except Exception, e:
            if e:
                date_data = fields[3]
                time = fields[4]
                print in_day
                print date_data
                print time
                if time.find('In') !=-1:
                    date_time_in = date_data
                    time_in = True
                    print 'in time',date_time_in
                    local_date_entry = None
                    try:
                        local_date_entry = datetime.strptime(date_time_in, '%d-%b-%y %H:%M:%S AM')
                    except Exception, e:
                        if date_time_in.find('AM')!=-1:
                            local_date_entry = datetime.strptime(date_time_in, '%m/%d/%Y %H:%M:%S AM') 
                            dt = input_tz.localize(local_date_entry, is_dst=False)
                        # And convert to UTC before reformatting for writing
                            utc_date_entry=dt.astimezone(pytz.UTC)
                            utc_date_entry_str = dt.astimezone(pytz.UTC).strftime('%m/%d/%Y %H:%M:%S AM')
                            print utc_date_entry_str
                            date_only = utc_date_entry.strftime("%m/%d/%Y")
                            time_entry = utc_date_entry.strftime("%H:%M:%S")
                            action_desc = 'inTime'
                            vals={}
                            vals['id'] = emp_id
                            vals['Name'] = emp_name
                            vals['action'] = 'inTime'
                            vals['aDate'] = utc_date_entry_str
                            vals['inTime'] = time_entry
                            vals['date'] = date_only
                            vals['in_day'] = in_day
                            in_exist = False
                            for att in attendances:
                                if int(att['id']) == emp_id and att['date'] == date_only and att['action'] != action_desc:
                                    att[action_desc] = time_entry
                                    in_exist = True;
                                    break;
                                    
                            if not in_exist:
                                    attendances.append(vals)
                                    print 'this is in time',time
                                    return attendances
                        elif date_time_in.find('PM')!=-1:
                            local_date_entry = datetime.strptime(date_time_in, '%m/%d/%Y %H:%M:%S PM')
                        
                            dt = input_tz.localize(local_date_entry, is_dst=False)
                        # And convert to UTC before reformatting for writing
                            utc_date_entry=dt.astimezone(pytz.UTC)
                            utc_date_entry_str = dt.astimezone(pytz.UTC).strftime('%m/%d/%Y %H:%M:%S PM')
                            print utc_date_entry_str
                            date_only = utc_date_entry.strftime("%m/%d/%Y")
                            time_entry = utc_date_entry.strftime("%H:%M:%S")
                            action_desc = 'inTime'
                    
                            vals={}
                            vals['id'] = emp_id
                            vals['Name'] = emp_name
                            vals['action'] = 'inTime'
                            vals['aDate'] = utc_date_entry_str
                            vals['inTime'] = time_entry
                            vals['date'] = date_only
                            vals['in_day'] = in_day
                    #this is code check if there contained any attendance same line
                            in_exist = False
                            for att in attendances:
                                if int(att['id']) == emp_id and att['date'] == date_only and att['action'] != action_desc:
                                    att[action_desc] = time_entry
                                    in_exist = True;
                                    break;
                                    
                            if not in_exist:
                                    attendances.append(vals)
                                    print 'this is in time',time
                                    return attendances
                elif time.find('Out') !=-1:
                    date_time_out = date_data
                    print 'out time',date_time_out
                    time_out = True
                    local_date_entry_out = None
                    try:
                        local_date_entry_out = datetime.strptime(date_time_out, '%d-%b-%y:%M:%S PM')
                    except Exception, e:
                        print e,date_time_out
                        if date_time_out.find('AM')!=-1:
                            local_date_entry_out = datetime.strptime(date_time_out, '%m/%d/%Y %H:%M:%S AM') 
                            dt_out = input_tz.localize(local_date_entry_out, is_dst=False)
                        # And convert to UTC before reformatting for writing
                #             utc_date_entry=dt_out.astimezone(pytz.UTC)
                            utc_date__out_entry=dt_out.astimezone(pytz.UTC)
                            utc_date_entry_out_str = dt_out.astimezone(pytz.UTC).strftime('%m/%d/%Y %H:%M:%S AM')
                            date_only = utc_date__out_entry.strftime("%m/%d/%Y")
                
                            date_out_only = utc_date__out_entry.strftime("%m/%d/%Y")
                            time_entry_out = utc_date__out_entry.strftime("%H:%M:%S")
                            action_desc = 'outTime'
                            out_vals={}
                            out_vals['id'] = emp_id
                            out_vals['Name'] = emp_name
                            out_vals['action'] = action_desc
                            out_vals['aDate'] = utc_date_entry_out_str
                            out_vals['outTime'] = time_entry_out##that my fix
                            out_vals['date'] = date_only
                            out_vals['in_day'] = in_day
                            attendances.append(out_vals)
                            return attendances
                        elif date_time_out.find('PM')!=-1:
                            local_date_entry_out = datetime.strptime(date_time_out, '%m/%d/%Y %H:%M:%S PM')
                            dt_out = input_tz.localize(local_date_entry_out, is_dst=False)
                        # And convert to UTC before reformatting for writing
                #             utc_date_entry=dt_out.astimezone(pytz.UTC)
                            utc_date__out_entry=dt_out.astimezone(pytz.UTC)
                            utc_date_entry_out_str = dt_out.astimezone(pytz.UTC).strftime('%m/%d/%Y %H:%M:%S PM')
                            date_only = utc_date__out_entry.strftime("%m/%d/%Y")
                
                            date_out_only = utc_date__out_entry.strftime("%m/%d/%Y")
                            time_entry_out = utc_date__out_entry.strftime("%H:%M:%S")
                            action_desc = 'outTime'
                    
                            out_vals={}
                            out_vals['id'] = emp_id
                            out_vals['Name'] = emp_name
                            out_vals['action'] = action_desc
                            out_vals['aDate'] = utc_date_entry_out_str
                            out_vals['outTime'] = time_entry_out##that my fix
                            out_vals['date'] = date_only
                            out_vals['in_day'] = in_day
                            attendances.append(out_vals)
                            print 'this is out time',time
                            return attendances
 
    def prepared_name_attendance(self, fields, input_tz, attendances):
        print 'fields',fields
        action_desc = ""
        time=fields[4]
        local_date_entry = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
        dt = input_tz.localize(local_date_entry, is_dst=False)
    # And convert to UTC before reformatting for writing
        utc_date_entry=dt.astimezone(pytz.UTC)
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
        emp_name = fields[1];  
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
        utc_date_entry=dt.astimezone(pytz.UTC)
        utc_date_entry_str = dt.astimezone(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S')
        date_only = utc_date_entry.strftime("%Y-%m-%d")
        time_entry = utc_date_entry.strftime("%H:%M:%S")
        vals = {}
        print "fields:",fields
        print "field3:", fields[3]
            
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
            
        emp_id = int(fields[2])
        #emp_name = fields[1];  
        exist = False
        for att in attendances:
            if int(att['id']) == emp_id and att['date'] == date_only:
                exist = True
            if int(att['id']) == emp_id and att['date'] == date_only and att['action'] != action_desc:
                att[action_desc] = time_entry
        
        vals['id'] = int(fields[2])
       # vals['Name'] = fields[1]
        vals['action'] = action_desc
        vals['aDate'] = utc_date_entry_str
        vals[action_desc] = time_entry
        vals['date'] = date_only
        if not exist:
                attendances.append(vals)
                return attendances
    def prepared_attendance_dat(self, cr,uid,lines,context=None):
        attendances = []
        input_tz = self._input_tz(cr, uid, context)# Apply input tz to the parsed naive datetime
        for line in lines:
            fields = line.split('\t')
            print 'fields',fields
            if len(fields) == 5:
                self.prepared_name_attendance(fields,input_tz,attendances)
            elif len(fields) == 6: 
                self.prepared_wihtoutname_attendance(fields,input_tz,attendances)
 
        return attendances
    def prepared_attendance_csv(self, cr,uid,amls,context):
        attendances = []
        input = self._input_tz(cr, uid, context)# Apply input tz to the parsed naive dat
      #  print 'fields',fields
        if amls:
            self.prepared_name_attendance_csv(cr,uid,amls,input,attendances,context)
  
        return True
                
    def prepared_attendance(self, cr,uid,lines,excel_import_file,context=None):
        attendances = []
        input_tz = self._input_tz(cr, uid, context)# Apply input tz to the parsed naive datetime
        for line in lines:
            if excel_import_file and line:
                self.prepared_attendance_excel(line,input_tz,attendances)
            else:
                fields = line.split('\t')
                if len(fields) == 5:
                    self.prepared_name_attendance(fields,input_tz,attendances)
                elif len(fields) == 6: 
                    self.prepared_wihtoutname_attendance(fields,input_tz,attendances)
        return attendances
    

  
    
    # Created by Thiha (11-Dec-2013)
    def create_att_new(self, cr, uid, lines,excel_import_file, context):
        employee_pool = self.pool.get("hr.employee")
        emp_fingerprint = {}
        emp_ids = employee_pool.search(cr, uid, [])
        hr_emp_data = employee_pool.read(cr, uid, emp_ids, ['id', 'fingerprint_id'])#fix
        from_date  = context['attendance_date']
        to_date = context['attendance_date_to']
        company_id=context['company_id'].id#fix
        for emp in hr_emp_data:
            if emp['fingerprint_id']:
                emp_fingerprint[int(emp['fingerprint_id'])] = emp['id']  
        attendances = self.prepared_attendance(cr, uid, lines,excel_import_file, context)
        print "Total Number of attendance records %d" % len(attendances)
        
        invalid_ids = []
        name_exist = False;
       
        if attendances:   
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
                            employee_ids = [employee_pool.create(cr, uid, {'name': employee_code, 'fingerprint_id':attance_line['id']})]
                            employee_id = employee_ids[0].id
                            emp_fingerprint[attance_line['id']] = employee_id
                        else:
                            cr.execute("select id from hr_employee where fingerprint_id = %s", (str(attance_line['id']).split()))
                            employee_id = cr.fetchone()[0]
                            
                    elif int(attance_line['id']) in emp_fingerprint:
                        employee_id = emp_fingerprint[int(attance_line['id'])]
                    in_day = None   
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
                    
                    if employee_code and employee_id and from_date<=to_date:# a little fix
                        self.create_attendance_line(cr, uid, employee_id, entry_date, in_time, out_time , break_out_time ,break_in_time , employee_code,company_id)
                        
                except Exception, e:
                    logger.error('Error %s', e)
                
        if len(invalid_ids) > 0 and name_exist == False:
            raise osv.except_osv(('Invalid Id[s]!'), ('User Id[s]: %s are not register as users!!' % (invalid_ids)))
        logger.info("Import Attendance Completed.")
        return True
    
    def prepared_name_attendance_csv(self, cr,uid,amls, input_tz, attendances,context=None):
        print 'fields',amls
        hr_employee_obj = self.pool.get('hr.employee')
        hr_att_obj = self.pool.get('hr.attendance')
        
        local_date_entry =None
        action_desc = ""
        for aml in amls:
            print 'aml',len(aml)
            att_id = emp_id = time_in = time_out = time_date = None
            emp_name = aml['Name']
            id = aml['Ac-No']
            time  = aml['sTime']
            if emp_name :
                emp_id = hr_employee_obj.search(cr,uid,[('name','=',emp_name),('fingerprint_id','=',id)])
                if not emp_id:
                    emp_value = {'fingerprint_id':id,'name':emp_name}
                    emp_ids = hr_employee_obj.create(cr,uid,emp_value,context=context)
                else:
                    emp_ids = emp_id[0]
            if emp_ids :
                att_id =hr_att_obj.search(cr,uid,[('employee_id','=',emp_ids)])
                if not att_id:
                    print 'hellosssss'

            if time:
                local_date_entry = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
                dt = input_tz.localize(local_date_entry, is_dst=False)
        # And convert to UTC before reformatting for writing
                utc_date_entry=dt.astimezone(pytz.UTC)
                utc_date_entry_str = dt.astimezone(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S')
                date_only = utc_date_entry.strftime("%Y-%m-%d")
                time_in = local_date_entry.strftime("%H:%M:%S")
                time_in_in = datetime.strptime(time_in, "%H:%M:%S").strftime("%H:%M:%S")
                print 'date_only',date_only,' and time_entry',time_in
                if time_in:
                    att_id = hr_att_obj.search(cr,uid,['&',('employee_id','=',emp_ids),('name','=',date_only+' '+time_in_in),('action','=','sign_in')])
                    if not att_id:
                        att_value = {'employee_id':emp_ids,'name':date_only+' '+str(time_in_in),'action':'sign_in'}
                        att_ids = hr_att_obj.create(cr,uid,att_value,context=context)
                    else:
                        att_ids =att_id[0]                

        return True