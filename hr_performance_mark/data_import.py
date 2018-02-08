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

header_fields = ['fingerprint_id', 'badge_id', 'date', 'mark', 'reason','code']

class employee_performance_mark_info(osv.osv):
    _name = 'data_import.performance_mark'
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
    
    _constraints = [(_check_file_ext, "Please import EXCEL file!", ['import_fname'])]
    
    def import_data(self, cr, uid, ids, context=None):
        hr_employee_obj = self.pool.get('hr.employee')
        hr_performance_obj = self.pool.get('hr.performance.mark')
        data = self.browse(cr, uid, ids)[0]
        company_id = data.company_id.id
        import_file = data.import_file
        m = f = None        
                                                                             
        err_log = ''
        header_line = False
        value = {}
        lines = base64.decodestring(import_file)
        wb = open_workbook(file_contents=lines)
        excel_rows = []
        for s in wb.sheets():
            # header
            headers = []
            header_row = 0
            for hcol in range(0, s.ncols):
                headers.append(s.cell(header_row, hcol).value)
            # add header
            excel_rows.append(headers)
            for row in range(header_row + 1, s.nrows):
                values = []
                for col in range(0, s.ncols):
                    values.append(s.cell(row, col).value)
                excel_rows.append(values)
        con_ls = []
        amls = []
        arr_payslip_id = []
        count = val = head_count = 0
        for ln in excel_rows:
            # ln = [str(x).strip() for x in ln] #add
            if not ln or ln and ln in ['', '#']:
                continue
            # process header line
            
            if not header_line:
                for x in ln:
                    x = str(x).strip().lower()
                    if x in header_fields:
                        con_ls.append(x)
                        head_count = head_count + 1
#                 if head_count < 5:
#                     head_count = 0
#                     con_ls=[]
#                 else:
                if ln:
                    b3 = set(header_fields).difference(con_ls)
                    # check the columns without contained the header fields
                    if b3:
                        for l in b3:
                            ln.append(str(l))
                        val = len(b3)
                    header_line = True

                    
                    fingerprint_id_i = badge_id_i = date_i = mark_i= reason_i = code_i= None
                    column_cnt = len(ln)
                    
                    for i in range(column_cnt):
                        header_field = ln[i]                        
                        if header_field not in header_fields:
                            err_log += '\n' + _("Invalid Excel File, Header Field '%s' is not supported !") % ln[i]
                        # required header fields : account, debit, credit
                                                    
                        elif header_field == 'fingerprint_id':
                            fingerprint_id_i = i
                        elif header_field == 'badge_id':
                            badge_id_i = i
                        elif header_field == 'date':
                            date_i = i
                        elif header_field == 'mark':
                            mark_i = i                                                       
                        elif header_field == 'reason':
                            reason_i = i                              
                        elif header_field == 'code':
                            code_i = i                                               
                # process data lines   
            else:
                # add the without value for without header fields columns
                for i in range(0, val):
                    ln.append('')
                if ln and ln not in ['#', '']:
                    
                    import_vals = {}
                    import_vals['fingerprint_id'] = ln[fingerprint_id_i]                    
                    import_vals['badge_id'] = ln[badge_id_i]                    
                    import_vals['date'] = ln[date_i]
                    import_vals['mark'] = ln[mark_i]
                    import_vals['reason'] = ln[reason_i]
                    import_vals['code'] = ln[code_i]
                    amls.append(import_vals)
                    
        if err_log:
            self.write(cr, uid, ids[0], {'note': err_log})
            self.write(cr, uid, ids[0], {'state': 'error'})
        if amls:
        # if amls :    
            for aml in amls:
                
                fingerprint_id = badge_id = date = out_time = reason = code = None
                value = {}
                
                print 'aml', aml
                if aml['fingerprint_id']:
                    try:
                        fingerprint_id = str(aml['fingerprint_id'].encode('utf-8')).strip()
                    except Exception, e:
                        fingerprint_id = str(aml['fingerprint_id']).strip()
                        fingerprint_id = fingerprint_id.replace('.0', '')
                else:
                    fingerprint_id = None
                emp_ids = None
                if fingerprint_id:
                    cr.execute('select id from hr_employee where fingerprint_id= %s', (fingerprint_id.lower(),))
                    emp_ids = cr.fetchall()                    
                       
                if aml['badge_id']:
                    badge_id = aml['badge_id']
                    
                else:
                    badge_id = 0
                                                                                 
                if aml['date']:
                    try:
                        data_time = float(aml['date'])
                        result = xlrd.xldate.xldate_as_tuple(data_time, 0)
                        a = str(result[1]) + '/' + str(result[2]) + '/' + str(result[0]) + ' ' + str(result[3]) + ':' + str(result[4]) + ':' + str(result[5])
                        date = datetime.strptime(a, '%m/%d/%Y %H:%M:%S').date()
                    except Exception , e:
                        try:
                            str_date = str(aml['date']).strip() + ' 00:00:00'
                            date = datetime.strptime(str_date, '%m/%d/%Y %H:%M:%S').date()
                        except Exception, e:
                            try:
                                str_date = str(aml['date']).strip() + ' 00:00:00'
                                date = datetime.strptime(str_date, '%Y/%m/%d %H:%M:%S').date()
                            except Exception, e:
                                try:
                                    str_date = str(aml['date']).strip() + ' 00:00:00'
                                    date = datetime.strptime(str_date, '%d/%m/%Y %H:%M:%S').date()
                                except Exception, e:
                                    try:
                                        date = None
                                    except Exception, e:
                                        raise orm.except_orm(_('Error :'), _("Error while processing Excel Columns. \n\nPlease check your effective date!"))
                
                if aml['mark']:
                    mark = float(aml['mark'])
                else:
                    mark = 0
                    
                if aml['reason']:
                    reason = aml['reason']
                else:
                    reason = 0            
                      
                if aml['code']:
                    code = aml['code']
                else:
                    code = None
                                                                                      
                if emp_ids:
                    employee = hr_employee_obj.browse(cr, uid, emp_ids[0], context=context)
                    department_id = employee.department_id.id
                    job_id = employee.job_id.id
                    section_id = employee.section_id.id
                    badge_id = employee.employee_id          
                    cr.execute("delete from hr_performance_mark where date =%s  and employee_id =%s and code=%s",(date,emp_ids[0],code,))          
                    hr_performance_obj.create(cr, uid, {
                                                  'employee_id': emp_ids[0],
                                                  'badge_id': badge_id,
                                                  'department_id':department_id,
                                                 'section_id':section_id,
                                                  'job_id':job_id,
                                                  'date':date,
                                                  'mark':mark,
                                                  'note':reason,
                                                  'code':code,
                                                  }, context=context)

                                               
            self.write(cr, uid, ids[0], {'state': 'completed'})
         
 
  
# Under class is for hr_contract
