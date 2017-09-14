from openerp.osv import orm
from openerp.osv import fields, osv
import xlrd
import codecs
from xlrd import open_workbook
from openerp.tools.translate import _
from datetime import datetime
import base64
import logging
import time

_logger = logging.getLogger(__name__)
header_fields = ['employee/name', 'description', 'date', 'expense lines/date', 'expense lines/times', 'expense lines/uniform name/uniform name', 'expense lines/quantities', 'expense lines/unit price', 'expense lines/total', 'job positions/job name', 'department/department name', 'paid amount', 'payment lines/date', 'payment lines/is paid', 'payment lines/pay amount', 'payment lines/payment type']
class uniform(osv.osv):
    _name = 'data_import.uniform'
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
    def import_data(self, cr, uid, ids, context=None):
        hr_employee_obj = self.pool.get('hr.employee')
        hr_ulm_expense_obj = self.pool.get('hr.ulm.expense')
        hr_ulm_expense_line_obj = self.pool.get('hr.ulm.expense.line')
        uniform_name_obj = self.pool.get('uniform.name')
        hr_ulm_payment_obj = self.pool.get('hr.ulm.payment')
        data = self.browse(cr, uid, ids)[0]
        import_file = data.import_file
        err_log = ''
        header_line = False
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
        count = val = head_count = 0
        for ln in excel_rows:
            # ln = [str(x).strip() for x in ln]
            if not ln or ln and ln in ['', '#']:
                continue
            # process header line
            
            if not header_line:
                for x in ln:
                    x = str(x).strip().lower()
                    if x in header_fields:
                        con_ls.append(x)
                        head_count = head_count + 1
                if head_count < 5:
                    head_count = 0
                    con_ls = []
                else:
                    if ln:
                        b3 = set(header_fields).difference(con_ls)
                        # check the columns without contained the header fields
                        if b3:
                            for l in b3:
                                ln.append(str(l))
                            val = len(b3)
                    header_line = True
                    # day_plan_i = sale_team_i = customer_code_i = main_group_i = date_i = branch_i = None
                    employee_name_i = description_i = date_i = expenselinesdate_i = expenselinestimes_i = expenselinesuniformname_i = expenselinesquantities_i = expenselinesunitprice_i = expenselinestotal_i = jobpositionsjobname_i = departmentname_i = paidamount_i = paymentlinesdate_i = paymentlinesispaid_i = paymentlinespayamount_i = paymentlinespaymenttype_i = None
                    column_cnt = len(ln)
                    for i in range(column_cnt):
                        # header fields
                        header_field = ln[i].strip().lower()
                        if header_field not in header_fields:
                            err_log += '\n' + _("Invalid Excel File, Header Field '%s' is not supported !") % ln[i]
                        # required header fields : account, debit, credit
                        elif header_field == 'employee/name':
                            employee_name_i = i
                        elif header_field == 'description':
                            description_i = i
                        elif header_field == 'date':
                            date_i = i
                        elif header_field == 'expense lines/date':
                            expenselinesdate_i = i
                        elif header_field == 'expense lines/times':
                            expenselinestimes_i = i
                        elif header_field == 'expense lines/uniform name/uniform name':
                            expenselinesuniformname_i = i
                        elif header_field == 'expense lines/quantities':
                            expenselinesquantities_i = i
                        elif header_field == 'expense lines/unit price':
                            expenselinesunitprice_i = i
                        elif header_field == 'expense lines/total':
                            expenselinestotal_i = i
                        elif header_field == 'job positions/job name':
                            jobpositionsjobname_i = i
                        elif header_field == 'department/department name':
                            departmentname_i = i
                        elif header_field == 'paid amount':
                            paidamount_i = i
                        elif header_field == 'payment lines/date':
                            paymentlinesdate_i = i
                        elif header_field == 'payment lines/is paid':
                            paymentlinesispaid_i = i
                        elif header_field == 'payment lines/pay amount':
                            paymentlinespayamount_i = i
                        elif header_field == 'payment lines/payment type':
                            paymentlinespaymenttype_i = i
                                                               
                    # for f in [(day_plan_i, 'day'), (sale_team_i, 'sale_team'), (customer_code_i, 'customer_code'), (main_group_i, 'main_group'), (date_i, 'date'), (branch_i, 'branch')]:
                    for f in [(employee_name_i, 'employee/name'), (description_i, 'description'), (date_i, 'date'), (expenselinesdate_i, 'expense lines/date'), (jobpositionsjobname_i, 'job positions/job name'), (departmentname_i, 'department/department name'), (expenselinesquantities_i, 'expense lines/quantities'), (expenselinesuniformname_i, 'expense lines/uniform name/uniform name'), (expenselinestimes_i, 'expense lines/times'), (expenselinesunitprice_i, 'expense lines/unit price'), (expenselinestotal_i, 'expense lines/total'), (paidamount_i , 'paid amount')]:    
                        if not isinstance(f[0], int):
                            err_log += '\n' + _("Invalid Excel file, Header '%s' is missing !") % f[1]
                        
                # process data lines   
            else:
                # add the without value for without header fields columns
                for i in range(0, val):
                    ln.append('')
                if ln and ln[0] and ln[0][0] not in ['#', '']:
                    import_vals = {}
                    import_vals['employee_name'] = ln[employee_name_i]
                    import_vals['description'] = ln[description_i]
                    import_vals['date'] = ln[date_i]
                    import_vals['expense_lines_date'] = ln[expenselinesdate_i]
                    import_vals['jobname'] = ln[jobpositionsjobname_i]
                    import_vals['department_name'] = ln[departmentname_i]
                    import_vals['expense_lines_quantities'] = ln[expenselinesquantities_i]
                    import_vals['expense_lines_uniform_name'] = ln[expenselinesuniformname_i]
                    import_vals['expense_lines_times'] = ln[expenselinestimes_i]
                    import_vals['expense_lines_unit_price'] = ln[expenselinesunitprice_i]
                    import_vals['expense_lines_total'] = ln[expenselinestotal_i]
#                     import_vals['payment_lines_date'] = ln[paymentlinesdate_i]
#                     import_vals['payment_lines_ispaid_'] = ln[paymentlinesispaid_i]
#                     import_vals['payment_lines_payamount'] = ln[paymentlinespayamount_i ]
#                     import_vals['payment_lines_paymenttype'] = ln[paymentlinespaymenttype_i]
                    
                    amls.append(import_vals)
                    print 'exvel'  ,amls
        if err_log:
            self.write(cr, uid, ids[0], {'note': err_log})
            self.write(cr, uid, ids[0], {'state': 'error'})
        if amls or err_log:
            
            try:
                for aml in amls:
                   
                    # day_plan = sale_team = sale_team_id = customer_code = main_group = main_group_id = date = branch = branch_id = plan_id = customer_id = customer_code = None
                    emp_id = job_id = dep_id = date_data = employee_name = description = job_name = department_name = date = expenselinesdate = expenselinestimes = expenselinesuniformname = expenselinesquantities = expenselinesunitprice = expenselinestotal = jobpositionsjobname = paidamount = paymentlinesdate = paymentlinesispaid = paymentlinespayamount = paymentlinespaymenttype = None
                    data = None
                    
                    if aml['employee_name'] != None and aml['jobname'] != None and aml['department_name'] != None:
                        try:
                            
                            employee_name = str(aml['employee_name']).strip()
                            job_name = str(aml['jobname']).strip()
                            department_name = str(aml['department_name']).strip()
                            cr.execute("""select emp.id,emp.job_id,emp.department_id from  hr_employee emp,hr_job job,hr_department dep 
                                where emp.job_id = job.id and emp.department_id = dep.id 
                                and lower(emp.name_related)=%s and lower(job.name)=%s and lower(dep.name)=%s""", (employee_name.lower(), job_name.lower(), department_name.lower(),))
                            emp_data = cr.fetchall()
                            print 'emp_data', emp_data
                            if emp_data:
                                
                                emp_id = emp_data[0][0]
                                job_id = emp_data[0][1]
                                dep_id = emp_data[0][2]
                        except Exception , e:
                            try:
                                
                                employee_name = aml['employee_name'].encode('utf-8').strip()
                                job_name = str(aml['jobname']).strip()
                                department_name = str(aml['department_name']).strip()
                                print 'employee_name',employee_name,job_name,department_name
                                
#                                 cr.execute("""select emp.id,emp.job_id,emp.department_id from  hr_employee emp,hr_job job,hr_department dep 
#                                 where emp.job_id = job.id and emp.department_id = dep.id 
#                                 and emp.name_related=%s and lower(job.name)=%s and lower(dep.name)=%s""",(employee_name,job_name.lower(),department_name.lower(),))
                                cr.execute("""select emp.id,emp.job_id,emp.department_id from  hr_employee emp,hr_job job,hr_department dep 
                                where emp.job_id = job.id and emp.department_id = dep.id 
                                and emp.name_related like %s and lower(job.name) = %s """, (employee_name.lower(),job_name.lower(),))
                                
                                emp_data = cr.fetchall()
                                print 'emp_data', emp_data
                                if emp_data:
                                    print 'assign employee from mm'
                                    emp_id = emp_data[0][0]
                                    job_id = emp_data[0][1]
                                    dep_id = emp_data[0][2]
                                    
                            except Exception , e:
                                print 'Exception', e
                                
                                
                                
                    else:
                        employee_name = None
                        job_name = None
                        department_name = None
                    
#                     if aml['payment_lines_ispaid_']:
#                         paymentlinesispaid = str(aml['payment_lines_ispaid_']).strip()
#                     else:
#                         paymentlinesispaid = None
#                     
#                     if aml['payment_lines_payamount']:
#                         paymentlinespayamount  = str(aml['payment_lines_payamount']).strip()
#                     else:
#                         paymentlinespayamount  = None
#                     print 'aml[payment_lines_paymenttype]>>>>',aml['payment_lines_paymenttype']
#                     if aml['payment_lines_paymenttype']:
#                         paymentlinespaymenttype = str(aml['payment_lines_paymenttype']).strip()
#                     else:
#                         paymentlinespaymenttype = None 
                                   
                    if aml['expense_lines_uniform_name']:
                        try:
                            expenselinesuniformname = aml['expense_lines_uniform_name'].strip()
                            cr.execute('select id from uniform_name where  lower(name)= %s', (expenselinesuniformname.lower(),))
                            uniform_data = cr.fetchall()
                            if uniform_data :
                                uniform_id = uniform_data[0]
                            else:
                                
                                uniform_id = uniform_name_obj.create(cr, uid, {'name': expenselinesuniformname}, context=context)
                                  
                        except Exception , e: 
                            try:
                                
                                expenselinesuniformname = aml['expense_lines_uniform_name'].encode('utf-8').strip()
                               
                                cr.execute('select id from uniform_name where  name= %s', (expenselinesuniformname,))
                                uniform_data = cr.fetchall()
                                if uniform_data :
                                    uniform_id = uniform_data[0]
                                else:
                                   
                                    uniform_id = uniform_name_obj.create(cr, uid, {'name': expenselinesuniformname}, context=context)
                                   
                            except Exception , e:         
                                
                                print 'Exception', e 
                    else : 
                        expenselinesuniformname = None 
                           
                    if aml['description']:
                        description = str(aml['description']).strip()
                    else:
                        description = None
                            
                    if aml['expense_lines_times']:
                        expenselinestimes = str(aml['expense_lines_times']).strip()
                    else:
                        expenselinestimes = None
                    
                    if aml['expense_lines_quantities']:
                        expenselinesquantities = str(aml['expense_lines_quantities']).strip()
                    else:
                        expenselinesquantities = None
                        
                    if aml['expense_lines_unit_price']:
                        expenselinesunitprice = str(aml['expense_lines_unit_price']).strip()
                    else:
                        expenselinesunitprice = None
                        
                    if aml['expense_lines_total']:
                        expenselinestotal = str(aml['expense_lines_total']) .strip()
                    else:
                        expenselinestotal = None
                    
#                     if aml['paid_amount']:
#                         paidamount = str(aml['paid_amount']).strip()
#                         print 'paidamount>>>',paidamount
                    
                                              
                    if aml['date']:
                        try:
                            data_time = float(aml['date'])
                            result = xlrd.xldate.xldate_as_tuple(data_time, 0)
                            a = str(result[1]) + '/' + str(result[2]) + '/' + str(result[0]) + ' ' + str(result[3]) + ':' + str(result[4]) + ':' + str(result[5])
                            date_data = datetime.strptime(a, '%m/%d/%Y %H:%M:%S').date()
                        except Exception , e:
                            try:
                                str_date = str(aml['date']).strip() + ' 00:00:00'
                                date_data = datetime.strptime(str_date, '%m/%d/%Y %H:%M:%S').date()
                            except Exception, e:
                                try:
                                    str_date = str(aml['date']).strip() + ' 00:00:00'
                                    date_data = datetime.strptime(str_date, '%Y/%m/%d %H:%M:%S').date()
                                except Exception, e:
                                    try:
                                        str_date = str(aml['date']).strip() + ' 00:00:00'
                                        date_data = datetime.strptime(str_date, '%d/%m/%Y %H:%M:%S').date()
                                    except Exception, e:
                                        try:
                                            date_data = None
                                            
                                        except Exception, e:
                                            raise orm.except_orm(_('Error :'), _("Error while processing Excel Columns. \n\nPlease check your Date!"))
                    else: 
                        date_date = time.strftime("%Y-%m-%d")  # datetime.date.today()
                        
                        
#                     if aml['payment_lines_date']:
#                         print '>>>;',aml['payment_lines_date']
#                         try:
#                             payment_lines_data_time = float(aml['payment_lines_date'])
#                             print 'expense_lines_data_time',payment_lines_data_time
#                             result = xlrd.xldate.xldate_as_tuple(payment_lines_data_time, 0)
#                             print 'result ',result
#                             a = str(result[1]) + '/' + str(result[2]) + '/' + str(result[0]) + ' ' + str(result[3]) + ':' + str(result[4]) + ':' + str(result[5])
#                             payment_lines_data = datetime.strptime(a, '%m/%d/%Y %H:%M:%S').date()
#                             print 'expense_lines_data>>>', payment_lines_data
#                         except Exception , e:
#                             try:
#                                 payment_lines_date = str(aml['expense_lines_date']).strip() + ' 00:00:00'
#                                 payment_lines_data = payment_lines_data_time.strptime(payment_lines_date, '%m/%d/%Y %H:%M:%S').date()
#                             except Exception, e:
#                                 try:
#                                     str_date = str(aml['expense_lines_date']).strip() + ' 00:00:00'
#                                     payment_lines_data = payment_lines_data_time.strptime(payment_lines_date, '%Y/%m/%d %H:%M:%S').date()
#                                 except Exception, e:
#                                     try:
#                                         str_date = str(aml['expense_lines_date']).strip() + ' 00:00:00'
#                                         payment_lines_data = payment_lines_data_time.strptime(payment_lines_date, '%d/%m/%Y %H:%M:%S').date()
#                                     except Exception, e:
#                                         try:
#                                             payment_lines_data = None
#                                         except Exception, e:
#                                             raise orm.except_orm(_('Error :'), _("Error while processing Excel Columns. \n\nPlease check your Date!"))
                        
                    if aml['expense_lines_date']:
                        
                        try:
                            expense_lines_data_time = float(aml['expense_lines_date'])
                            
                            result = xlrd.xldate.xldate_as_tuple(expense_lines_data_time, 0)
                            
                            a = str(result[1]) + '/' + str(result[2]) + '/' + str(result[0]) + ' ' + str(result[3]) + ':' + str(result[4]) + ':' + str(result[5])
                            expense_lines_data = datetime.strptime(a, '%m/%d/%Y %H:%M:%S').date()
                            
                        except Exception , e:
                            try:
                                expense_lines_date = str(aml['expense_lines_date']).strip() + ' 00:00:00'
                                expense_lines_data = expense_lines_data_time.strptime(expense_lines_date, '%m/%d/%Y %H:%M:%S').date()
                            except Exception, e:
                                try:
                                    str_date = str(aml['expense_lines_date']).strip() + ' 00:00:00'
                                    expense_lines_data = expense_lines_data_time.strptime(expense_lines_date, '%Y/%m/%d %H:%M:%S').date()
                                except Exception, e:
                                    try:
                                        str_date = str(aml['expense_lines_date']).strip() + ' 00:00:00'
                                        expense_lines_data = expense_lines_data_time.strptime(expense_lines_date, '%d/%m/%Y %H:%M:%S').date()
                                    except Exception, e:
                                        try:
                                            expense_lines_data = None
                                        except Exception, e:
                                            raise orm.except_orm(_('Error :'), _("Error while processing Excel Columns. \n\nPlease check your Date!"))
                                        
                    if date_data == None:
                        
                        date_data = time.strftime("%Y-%m-%d") 
                   
                   
                    if emp_id and job_id and dep_id and date_data:
                        print 'data' ,date_data,emp_id,job_id,dep_id
                        cr.execute('select id from hr_ulm_expense where employee_id = %s and job_id= %s and department_id = %s  and date::date =%s ', (emp_id, job_id, dep_id, date_data,))
                        result = cr.fetchall()
                        print 'data' ,result
                        if not result:
                            print  'create'
                            uniexp_id = hr_ulm_expense_obj.create(cr, uid, {'name': description,
                                                                                        'employee_id':emp_id,
                                                                                        'job_id':job_id,
                                                                                        'date':date_data,
                                                                                        'department_id':dep_id,
                                                                                        'paid_amount':0                                                                                                                                                                                
                                                                                        }, context=context)
                            print 'done'
                            if uniexp_id:
                                print 'expenselinestimes',expenselinestimes ,expense_lines_data,uniform_id,expenselinesquantities,expenselinesunitprice
                                val=hr_ulm_expense_line_obj.create(cr, uid, {'date_value': expense_lines_data,
                                                                       'expense_id' : uniexp_id,
                                                                       'unit_amount' : expenselinesunitprice,
                                                                       'unit_quantity' : expenselinesquantities,
                                                                       'ref' : str(expenselinestimes),
                                                                       'name':uniform_id}, context=context)
                                
                                print 'paymentlinesispaid>>',expenselinestimes,val
#                                 hr_ulm_payment_obj.create(cr, uid, {'name': payment_lines_data,
#                                                                     'is_paid': False,#paymentlinesispaid,
#                                                                     'payment_type': paymentlinespaymenttype,
#                                                                     'expense_id': uniexp_id,
#                                                                     'amount': paymentlinespayamount}, context=context)
                        else:
                            print ' no_resut',emp_id,job_id,date_data,dep_id
                            uniexp_id = result[0][0]
                            
                            l=[]
                            l.append(uniexp_id)
                            hr_ulm_expense_obj.write(cr, uid, l, {'name': description,
                                                                                        'employee_id':emp_id,
                                                                                        'job_id':job_id,
                                                                                        'date':date_data,
                                                                                        'department_id':dep_id,
                                                                                        'paid_amount':0                                                                                                                                                                                
                                                                                        }, context=context)
                            print ' uniexp_id',uniexp_id,uniform_id,expenselinesquantities,expense_lines_data
                            cr.execute('delete from hr_ulm_expense_line where expense_id=%s and name=%s and unit_quantity =%s and date_value=%s',(uniexp_id,uniform_id,expenselinesquantities,expense_lines_data,))
                            
                            print ' expense_lines_data',expense_lines_data,expenselinesquantities,expenselinestimes
                            if uniexp_id:
                                hr_ulm_expense_line_obj.create(cr, uid, {'date_value': expense_lines_data,
                                                                       'expense_id' : uniexp_id,
                                                                       'unit_amount' : expenselinesunitprice,
                                                                       'unit_quantity' :expenselinesquantities ,
                                                                       'ref' : str(expenselinestimes),
                                                                       'name':uniform_id}, context=context)
                                print 'paymentlinesispaid>>',hr_ulm_expense_line_obj
#                                 hr_ulm_payment_obj.create(cr, uid, {'name': payment_lines_data,
#                                                                     'is_paid': paymentlinesispaid,
#                                                                     'payment_type': paymentlinespaymenttype,
#                                                                     'expense_id': uniexp_id,
#                                                                      'amount': paymentlinespayamount}, context=context)
                                
                self.write(cr, uid, ids, {'state':'completed'}, context=context)
                                     
            except Exception, e:
                raise osv.except_osv(_('Warning!'), _('Something wrong with this %s .') % (e))  
        
            
