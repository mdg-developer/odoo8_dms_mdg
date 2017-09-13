from openerp.osv import orm
from openerp.osv import fields, osv
import xlrd
import codecs
from xlrd import open_workbook
from openerp.tools.translate import _
from datetime import datetime
import base64
import logging
_logger = logging.getLogger(__name__)
#header_fields = ['function level','mgmt grade','effective date','last day of service date','business unit','cost of living allowance','qualifn. allowance','corporate title','functional title','fingerprint_id', 'employement status pse | pdwe', 'name', 'gender', 'marital status', 'designation','business unit','function',
#     'department', 'team', 'line responsibility','job family skill','father name','tax exemption for father','mother name'
#    , 'tax exemption for mother','spouse name','tax exemption for spouse','number of children under 18','number of children over 18 without income','nric','basic salary','highest qualification']
header_fields = ['fingerprint_id','temporary_out','date_from','date_to']

class employee_temporary_out(osv.osv):
    _name = 'data_import.temporary_out'
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
        hr_payslip_obj = self.pool.get('hr.payslip')
        #hr_payslip_worked_day_obj = self.pool.get('hr.payslip.worked.day')hr_payslip_input
        hr_payslip_input_obj = self.pool.get('hr.payslip.input')
        data = self.browse(cr,uid,ids)[0]
        company_id = data.company_id.id
        import_file = data.import_file
        m = f = None        
                                                                             
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
        con_ls =[]
        amls = []
        arr_payslip_id = []
        count = val = head_count = 0
        for ln in excel_rows:
            #ln = [str(x).strip() for x in ln] #add
            if not ln or ln and ln in ['', '#']:
                continue
            # process header line
            
            if not header_line:
                for x in ln:
                    x = str(x).strip().lower()
                    if x in header_fields:
                        con_ls.append(x)
                        head_count = head_count+1
#                 if head_count < 5:
#                     head_count = 0
#                     con_ls=[]
#                 else:
                if ln:
                    b3 =  set(header_fields).difference(con_ls)
                    # check the columns without contained the header fields
                    if b3:
                        for l in b3:
                            ln.append(str(l))
                        val = len(b3)
                    header_line = True

                    
                    fingerprint_id_i = temporary_out_i = number_of_hours_i = number_of_days_i = date_from_i = date_to_i = None
                    column_cnt = len(ln)
                    
                    for i in range(column_cnt):
                        # header fields
                        #print 'ln[i].strip().lower()',ln[i].strip().lower()
                        
                        header_field = ln[i]                        
                        if header_field not in header_fields:
                            err_log += '\n' + _("Invalid Excel File, Header Field '%s' is not supported !") %ln[i]
                        # required header fields : account, debit, credit
                                                    
                        elif header_field == 'fingerprint_id':
                            fingerprint_id_i = i
                            
                        elif header_field == 'temporary_out':
                            temporary_out_i = i
                                                                                               
                        elif header_field == 'date_from':
                            date_from_i = i
                        
                        elif header_field == 'date_to':
                            date_to_i = i                          
                        
                          
                    
                        
                #process data lines   
            else:
                # add the without value for without header fields columns
                for i in range(0, val):
                    ln.append('')
                if ln and ln not in ['#','']:
                    
                    import_vals = {}
                    import_vals['fingerprint_id'] =  ln[fingerprint_id_i]                    
                    import_vals['temporary_out'] = ln[temporary_out_i]                    
                    import_vals['date_from'] = ln[date_from_i]
                    import_vals['date_to'] = ln[date_to_i]
                   
                    amls.append(import_vals)
                    
        if err_log:
            self.write(cr, uid, ids[0], {'note': err_log})
            self.write(cr, uid, ids[0], {'state': 'error'})
        if amls:
        #if amls :    
            for aml in amls:
#                 job_family_skill = cost_of_living_allowance_id = business_unit = business_unit_id = last_day_of_service_date = effective_date = mgmt_grade = mgmt_grade_id = function_level = function_level_id =cost_of_living_allowance =emp_id =employement_id =con_id = fingerprint_id = f_id =employement = name = gender = gender_type =marital = designation = business = function = department = team =None
#                 corporate_title = function_title = contract_type = pay_ids = base_ids  =marital_status = line = skill = father = tax_father =tax_father_type =mother = tax_mother = tax_mother_type =spouse = tax_spouse =nric =highest_qual =None
                fingerprint_id = temporary_out = date_from = date_to = None
                value ={}
                
                print 'aml',aml
                if aml['fingerprint_id']:
                    try:
                        fingerprint_id =str(aml['fingerprint_id'].encode('utf-8')).strip()
                    except Exception,e:
                        fingerprint_id = str(aml['fingerprint_id']).strip()
                        fingerprint_id = fingerprint_id.replace('.0','')
                else:
                    fingerprint_id = None
                emp_ids = None
                if fingerprint_id:
                    cr.execute('select id from hr_employee where fingerprint_id= %s',(fingerprint_id.lower(),))
                    emp_ids = cr.fetchall()                    
                       
                if aml['temporary_out']:
                    temporary_out = aml['temporary_out']
                    
                else:
                    temporary_out = 0
                                                             
                if aml['date_from']:
                    try:
                        data_time = float(aml['date_from'])
                        result = xlrd.xldate.xldate_as_tuple(data_time, 0)
                        a = str(result[1]) + '/' + str(result[2]) + '/' + str(result[0]) + ' ' + str(result[3]) + ':' + str(result[4]) + ':' + str(result[5])
                        effective_date = datetime.strptime(a, '%m/%d/%Y %H:%M:%S').date()
                    except Exception , e:
                        try:
                            str_date = str(aml['date_from']).strip() + ' 00:00:00'
                            effective_date = datetime.strptime(str_date, '%m/%d/%Y %H:%M:%S').date()
                        except Exception, e:
                            try:
                                str_date = str(aml['date_from']).strip() + ' 00:00:00'
                                effective_date = datetime.strptime(str_date, '%Y/%m/%d %H:%M:%S').date()
                            except Exception, e:
                                try:
                                    str_date = str(aml['date_from']).strip() + ' 00:00:00'
                                    effective_date = datetime.strptime(str_date, '%d/%m/%Y %H:%M:%S').date()
                                except Exception, e:
                                    try:
                                        effective_date = None
                                    except Exception, e:
                                        raise orm.except_orm(_('Error :'), _("Error while processing Excel Columns. \n\nPlease check your effective date!"))
                
                if aml['date_to']:
                    try:
                        data_time = float(aml['date_to'])
                        result = xlrd.xldate.xldate_as_tuple(data_time, 0)
                        a = str(result[1]) + '/' + str(result[2]) + '/' + str(result[0]) + ' ' + str(result[3]) + ':' + str(result[4]) + ':' + str(result[5])
                        eff_date = datetime.strptime(a, '%m/%d/%Y %H:%M:%S').date()
                    except Exception , e:
                        try:
                            str_date = str(aml['date_to']).strip() + ' 00:00:00'
                            eff_date = datetime.strptime(str_date, '%m/%d/%Y %H:%M:%S').date()
                        except Exception, e:
                            try:
                                str_date = str(aml['date_to']).strip() + ' 00:00:00'
                                eff_date = datetime.strptime(str_date, '%Y/%m/%d %H:%M:%S').date()
                            except Exception, e:
                                try:
                                    str_date = str(aml['date_to']).strip() + ' 00:00:00'
                                    eff_date = datetime.strptime(str_date, '%d/%m/%Y %H:%M:%S').date()
                                except Exception, e:
                                    try:
                                        eff_date = None
                                    except Exception, e:
                                        raise orm.except_orm(_('Error :'), _("Error while processing Excel Columns. \n\nPlease check your effective date!"))
                payslip_id = None   
                if emp_ids:
                    cr.execute('select id from hr_payslip where employee_id=%s and date_from= %s and date_to=%s ',(emp_ids[0][0],effective_date,eff_date,))
                    slip_ids = cr.fetchall()
                    if slip_ids:
                        payslip_id = slip_ids[0][0]
                        arr_payslip_id.append(payslip_id)
                        
                    else:
                        payslip_id = None
                else:
                    print 'emp not found'
                    #function_level_id = None
                workd_id = None 
                if payslip_id:
                   
                    cr.execute ("""select id from hr_payslip_input where payslip_id= %s and code='GPTO'""",(payslip_id,))
                    workd_id = cr.fetchall()
                    
                if workd_id:  
                    cr.execute('update hr_payslip_input set amount=%s where id=%s',(temporary_out,workd_id[0][0],))
                    
                
                   
            if arr_payslip_id:
                
                for payslip in arr_payslip_id:                    
                    hr_payslip_obj.compute_sheet(cr, uid, payslip, context=context) 
                                               
            self.write(cr, uid, ids[0], {'state': 'completed'})
         
 
  
#Under class is for hr_contract
