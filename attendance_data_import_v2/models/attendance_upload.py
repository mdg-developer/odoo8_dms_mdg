from openerp.osv import orm
from openerp.osv import fields, osv
import xlrd
import codecs
from xlrd import open_workbook
from openerp.tools.translate import _
from datetime import datetime
import base64
import logging
import contextlib
import math
_logger = logging.getLogger(__name__)

header_fields = ['emp no.', 'ac-no.','no.', 'name', 'auto-assign', 'date', 'timetable',
    'on duty', 'off duty', 'clock in','clock out','normal','real time'
   , 'late','early','absent', 'ot time','work time','exception','must c/in','must c/out','department','ndays',
   'weekend','holiday','att_time','ndays_ot','weekend_ot','holiday_ot']

class data_import_attendance(osv.osv):
    _name = 'data_import.attendance'
    _columns = {
              'name':fields.char('Description'),
              'import_date':fields.date('Import Date', readonly=True),
              'import_fname': fields.char('Filename', size=128),
              'import_file':fields.binary('File', required=True),
              'note':fields.text('Log'),
              'company_id': fields.many2one('res.company', 'Company', required=False),
              'state':fields.selection([
                ('draft', 'Draft'),
                ('completed', 'Completed'),
                ('error', 'Error'),
            ], 'States'),
              
              }
    _defaults = {
            'state':'draft',
            'import_date':datetime.today(),
                 }
    
    def _check_file_ext(self, cursor, user, ids):
        for import_file in self.browse(cursor, user, ids):
            if '.xls' in import_file.import_fname:return True
            else: return False
        return True
    
    _constraints = [(_check_file_ext,"Please import EXCEL file!",['import_fname'])]
    
    def import_data(self, cr, uid, ids, context=None):
        hr_employee_obj = self.pool.get('hr.employee')
        hr_job_obj=self.pool.get('hr.job')
        company_obj = self.pool.get('res.company')
        res_partner_obj=self.pool.get('res.partner')
        attendance_data_import_obj = self.pool.get('attendance.data.import')
        hr_department_obj=self.pool.get('hr.department')
        hr_section_obj=self.pool.get('hr.section')
        hr_nrc_prefix_obj=self.pool.get('hr.nrc.prefix')
        res_partner_bank_obj=self.pool.get('res.partner.bank')

        hr_contract_obj=self.pool.get('hr.contract')
        data = self.browse(cr,uid,ids)[0]
        company_id = data.company_id.id
        import_file = data.import_file
        hr_recuritment_obj=self.pool.get('hr.recruitment.degree')
        err_log = ''
        header_line = False
        value={}
        lines = base64.decodestring(import_file)
        wb = open_workbook(file_contents = lines)
        excel_rows=[]
        for s in wb.sheets():
            #header
            headers=[]
            header_row=0
            for hcol in range(0,s.ncols):
                headers.append(s.cell(header_row,hcol).value)
            #add header
            excel_rows.append(headers)
            for row in range(header_row+1,s.nrows):
                values = []
                for col in range(0,s.ncols):
                    values.append(s.cell(row,col).value)
                excel_rows.append(values)
        amls = []

        for ln in excel_rows:
            print 'ln>>>',ln
            
            #if not ln or ln and ln[0] and ln[0] in ['', '#']:    
            if not ln or ln and ln[0] and ln[0][0] in ['', '#']:
                continue
            
            # process header line
            if not header_line:
                if ln[0].strip().lower() not in header_fields:
                    raise orm.except_orm(_('Error :'), _("Error while processing the header line %s. \n\nPlease check your Excel separator as well as the column header fields") %ln)
                else:
                    header_line = True
                    emp_no_i = ac_no_i = no_i = name_i = auto_assign_i = date_i = timetable_i = None
                    on_duty_i = off_duty_i = clock_in_i =clock_out_i =normal_i =real_time_i = None
                    late_i = early_i = absent_i  = ot_time_i = work_time_i =exception_i =must_c_in_i =must_c_out_i =department_i =ndays_i = None
                    weekend_i =holiday_i =att_time_i =ndays_ot_i =weekend_ot_i =holiday_ot = None
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
                        header_field = ln[i].strip().lower()
                        print 'header_field>>>',header_field
                        if header_field not in header_fields:
                            err_log += '\n' + _("Invalid Excel File, Header Field '%s' is not supported !") %ln[i]
                        # required header fields : account, debit, credit
                        
                        elif header_field == 'emp no.':
                            emp_no_i = i
                        elif header_field == 'ac-no.':
                            ac_no_i = i
                        elif header_field == 'no.':
                            no_i = i
                        elif header_field == 'name':
                            name_i = i
                        elif header_field == 'auto-assign':
                            auto_assign_i = i
                        elif header_field == 'date':
                            date_i = i
                        elif header_field == 'timetable':
                            timetable_i = i
                        elif header_field == 'on duty':
                            on_duty_i = i
                        elif header_field == 'off duty':
                            off_duty_i = i
                        elif header_field == 'clock in':
                            clock_in_i = i
                        elif header_field == 'clock out':
                            clock_out_i = i
                        elif header_field == 'normal':
                            normal_i = i
                        elif header_field == 'real time':
                            real_time_i = i  
                        elif header_field == 'late':
                            late_i = i
                        elif header_field == 'early':
                            early_i = i          
                        elif header_field =='absent':
                            absent_i = i
                        elif header_field == 'ot time':
                            ot_time_i = i    
                        elif header_field =='work time':
                            work_time_i = i
                        elif header_field =='exception':
                            exception_i = i
                        elif header_field =='must c/in':
                            must_c_in_i = i
                        elif header_field =='must c/out':
                            must_c_out_i = i
                        elif header_field =='department':
                            department_i =i
                        elif header_field =='ndays':
                            ndays_i = i
                        elif header_field == 'weekend':    
                            weekend_i = i
                        elif header_field == "holiday":
                            holiday_i = i
                        elif header_field == "att_time":
                            att_time_i = i 
                        elif header_field == "ndays_ot":
                            ndays_ot_i = i         
                        elif header_field == "weekend_ot":
                            weekend_ot_i = i 
                        elif header_field == "holiday_ot":
                            holiday_i = i                        
                    for f in [(emp_no_i,'emp no.'),(date_i,'date'),(timetable_i,'timetable')]:
                        if not isinstance(f[0],int):
                            err_log += '\n'+ _("Invalid Excel file, Header '%s' is missing !") % f[1]
                        
                #process data lines   
            else:
                print 'ln>>>',ln
                print 'ln[0]>>>',ln[0]
                print 'ln[0][0]>>>',ln[0][0]
                #if ln and ln[0] not in ['#', '']:
                if ln and ln[0] and ln[0][0] not in ['#','']:
                    
                    import_vals = {}
                    
                    import_vals['emp_no'] =  ln[emp_no_i].strip()
                    import_vals['ac_no'] =  ln[ac_no_i].strip()
#                     import_vals['no'] =  ln[no_i].strip()
#                     import_vals['name'] =  ln[name_i].strip()
#                     import_vals['auto_assign'] =  ln[auto_assign_i].strip()
                    import_vals['date'] = ln[date_i]
                    import_vals['timetable'] = ln[timetable_i].strip()                   
                    import_vals['on_duty'] = ln[on_duty_i]
                    import_vals['off_duty'] = ln[off_duty_i]
                    import_vals['clock_in'] = ln[clock_in_i].strip()
                    import_vals['clock_out'] = ln[clock_out_i].strip()
                    import_vals['normal']  = ln[normal_i]
                    import_vals['real_time'] = ln[real_time_i]
                    import_vals['late'] = ln[late_i].strip()
                    import_vals['early'] = ln[early_i].strip()
                    import_vals['absent'] = ln[absent_i].strip()
                    import_vals['ot_time'] = ln[ot_time_i].strip()
                    import_vals['work_time'] = ln[work_time_i].strip()
                    import_vals['exception'] = ln[exception_i]
                    import_vals['must_c_in'] = ln[must_c_in_i]
                    import_vals['must_c_out'] = ln[must_c_out_i]
                    import_vals['department'] =ln[department_i]
                    import_vals['ndays'] = ln[ndays_i].strip()

                    import_vals['weekend']=ln[weekend_i]
                    import_vals['holiday'] = ln[holiday_i]
                    import_vals['att_time']=ln[att_time_i]
                    import_vals['ndays_ot']= ln[ndays_ot_i]
                    import_vals['weekend_ot'] = ln[weekend_ot_i]
                    import_vals['holiday_ot'] = ln[holiday_i]
                    
                    amls.append(import_vals)
       
        if err_log:
            self.write(cr, uid, ids[0], {'note': err_log})
            self.write(cr, uid, ids[0], {'state': 'error'})
        else:
            for aml in amls:
                emp_no = ac_no = no = name = auto_assign = t_date = date = timetable = None
                on_duty = off_duty = clock_in =clock_out =normal =real_time = None
                late = late_tmp = early_tmp = early = absent  = ot_time_tmp = ot_time = work_time_tmp = work_time = exception_t =must_c_in =must_c_out =department = department_id =ndays = None
                weekend =holiday =att_time_tmp = att_time = att_time_tmp =ndays_ot =weekend_ot =holiday_ot = None
                 
                per_date = join_date =datetime.today()
                if aml['emp_no']:
                    emp_no = aml['emp_no']
                if aml['ac_no']:
                    ac_no = aml['ac_no']
                if aml['date']:    
                    t_date =aml['date']
                if aml['timetable']:    
                    timetable = aml['timetable']
                if aml['on_duty']:   
                    on_duty = aml['on_duty']
                if aml['off_duty']:    
                    off_duty = aml['off_duty']
                if aml['clock_in']:    
                    clock_in=aml['clock_in']
                if aml['clock_out']:    
                    clock_out=aml['clock_out']
                if aml['normal']:    
                    normal=aml['normal']
                if aml['real_time']:    
                    real_time = aml['real_time']
                if aml['late']:    
                    late_tmp = aml['late']
                    if late_tmp:
                        late_data = late_tmp.split(':')
                        if late_data:
                            late = int(late_data[0]) * 6
                            late += int(late_data[1])
                if aml['early']:       
                    early_tmp = aml['early']
                    if early_tmp:
                        early_data = early_tmp.split(':')
                        if early_data:
                            early = int(early_data[0]) * 6
                            early += int(early_data[1])        
                
                if aml['absent']:
                    absent = aml['absent']
                
                if aml['ot_time']:
                    ot_time_tmp =aml['ot_time']
                    if ot_time_tmp:
                        ot_time_data = ot_time_tmp.split(':')
                        if ot_time_data:
                            ot_time = int(ot_time_data[0]) * 60
                            ot_time += int(ot_time_data[1])
                if aml['work_time']:
                    work_time_tmp =aml['work_time']
                    if work_time_tmp:
                        work_time_data = work_time_tmp.split(':')
                        if work_time_data:
                            work_time = int(work_time_data[0]) * 60
                            work_time += int(work_time_data[1])
                if aml['exception']:        
                    exception_i = aml['exception']
                if aml['must_c_in']:    
                    must_c_in = aml['must_c_in']
                if aml['must_c_out']:    
                    must_c_out = aml['must_c_out']
                if aml['department']:    
                    department = aml['department']
                if aml['ndays']:    
                    ndays = aml['ndays']
                if aml['weekend']:   
                    weekend = aml['weekend']
                if aml['holiday']:    
                    holiday = aml['holiday']
                if aml['att_time']:   
                    att_time_tmp = aml['att_time'] 
                    
                    if att_time_tmp:
                        att_time_data = att_time_tmp.split(':')
                        if att_time_data:
                            att_time = int(att_time_data[0]) * 60
                            att_time += int(att_time_data[1])
                if aml['ndays_ot']:           
                    ndays_ot = math.floor(float(aml['ndays_ot']))
                if aml['weekend_ot']:   
                    weekend_ot = aml['weekend_ot']
                if aml['holiday_ot']:  
                    holiday_ot = aml['holiday_ot']
                if aml['date']:                            
                    date = self.get_date(cr, uid, ids, aml['date'], context)
#                 if aml['date']:
#                     t_date = aml['date']
#                     try:
#                         
#                         data_time = float(t_date)
#                         result= xlrd.xldate.xldate_as_tuple(data_time,0)
#                         a= str(result[1])+'/'+str(result[2])+'/'+str(result[0])+' '+str(result[3])+':'+str(result[4])+':'+str(result[5])
#                 
#                         date = datetime.strptime(a, '%m/%d/%Y %H:%M:%S').date()
#                     except Exception, e:
#                         try:
#                             str_date=str(t_date)+' 00:00:00'
#                             date=datetime.strptime(str_date,'%m/%d/%Y %H:%M:%S').date()
#                         except Exception, e:
#                             try:
#                                 str_date=str(t_date)+' 00:00:00'
#                                 date=datetime.strptime(str_date,'%Y/%m/%d %H:%M:%S').date()
#                             except Exception,e:
#                                 try:
#                                     str_date=str(t_date)+' 00:00:00'
#                                     join_date=datetime.strptime(str_date,'%d/%m/%Y %H:%M:%S').date()
#                                 except Exception, e:
#                                     try:
#                                         date=datetime.today().date()
#                                     except Exception, e:
#                                         raise orm.except_orm(_('Error :'), _("Error while processing Excel Columns. \n\nPlease check your Date!"))
                              
                if ac_no:
                    attendance_id=attendance_data_import_obj.search(cr,uid,[('fingerprint_id','=',ac_no),('date','=',date),('timetable','=',timetable),('state','=','draft')])
                    emp_id = hr_employee_obj.search(cr,uid,[('fingerprint_id','=',ac_no)])
                    if emp_id:
                        emp_data = hr_employee_obj.browse(cr,uid,emp_id,context=None)
                        if emp_data:
                            department = emp_data.department_id.id
                    
                        value={'employee_id':emp_id[0] ,
                               'fingerprint_id':ac_no,
                              'auto_assign':auto_assign,
                             'date':date,
                             'timetable':timetable,
                             'onduty': on_duty,
                             'offduty': off_duty,
                             'clockin': clock_in,
                             'clockout' : clock_out,
                             'normal': normal,
                             'realtime': real_time,
                             'late': late,
                             'early':early,
                             'absent': absent,
                             'ot_time': ot_time,
                             'work_time': work_time,
                             'exception': exception_t,
                             'must_in': must_c_in,
                             'must_out': must_c_out,
                             'department_id':department,
                             'ndays': ndays,
                             'weekend': weekend,
                             'holiday': holiday,
                             'att_time': att_time,
                             'ndays_ot': ndays_ot,
                             'weekend_ot': weekend_ot,
                             'holiday_ot': holiday_ot,
                             'state': 'draft'
                             }              
                        if not attendance_id:
                            print 'value>>>',value
                            attendance_id = attendance_data_import_obj.create(cr,uid,value, context)
                        else:
                            attendance_id = attendance_data_import_obj.write(cr,uid,attendance_id[0],value)
                                                 
            self.write(cr, uid, ids[0], {'state': 'completed'})
        print amls
        
    def get_date(self, cr, uid, ids, datestring, context=None):
        date_data = None
        
        if datestring:
            try:
                data_time = float(datestring)
                result = xlrd.xldate.xldate_as_tuple(data_time, 0)
                a = str(result[1]) + '/' + str(result[2]) + '/' + str(result[0]) + ' ' + str(result[3]) + ':' + str(result[4]) + ':' + str(result[5])
                date_data = datetime.strptime(a, '%m/%d/%Y %H:%M:%S').date()
            except Exception , e:
                try:
                    str_date = str(datestring).strip() + ' 00:00:00'
                    date_data = datetime.strptime(str_date, '%m/%d/%Y %H:%M:%S').date()
                    
                except Exception, e:
                    try:
                        str_date = str(datestring).strip() + ' 00:00:00'
                        date_data = datetime.strptime(str_date, '%Y/%m/%d %H:%M:%S').date()
                        
                    except Exception, e:
                        try:
                            str_date = str(datestring).strip() + ' 00:00:00'
                            date_data = datetime.strptime(str_date, '%d/%m/%Y %H:%M:%S').date()
                        except Exception, e:
                            try:
                                str_date = str(datestring).strip() + ' 00:00:00'
                                date_data = datetime.strptime(datestring, '%d-%b-%y').strftime('%Y-%m-%d')    
                            except Exception, e:
                                try:
                                    date_data = None
                                except Exception, e:
                                    raise orm.except_orm(_('Error :'), _("Error while processing Excel Columns. \n\nPlease check your Date!"))
                                
        print 'date_data>>>',date_data                    
        return date_data        