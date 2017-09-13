from openerp.osv import orm
from openerp.osv import fields, osv
from xlrd import open_workbook
from openerp.tools.translate import _
import base64
import logging
#from matplotlib.dates import date2num,num2date
import xlrd
from datetime import datetime
_logger = logging.getLogger(__name__)
header_fields = ['birthday_month','name', 'gender', 'marital', 'identification_id', 'mobile_phone', 'work_phone',
    'work_email', 'birthday', 'father_name','fingerprint_id','department'
   , 'job','address_home','blood_group','company','birth_place']

class employee(osv.osv):
    _name = 'data_import.employee'
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
          #  'import_date':datetime.date.today(),
                 }
    
    def _check_file_ext(self, cursor, user, ids):
        for import_file in self.browse(cursor, user, ids):
            if '.xls' in import_file.import_fname:return True
            else: return False
        return True
    
    _constraints = [(_check_file_ext,"Please import xls file!",['import_fname'])]
    
    def import_data(self, cr, uid, ids, context=None):
        hr_employee_obj = self.pool.get('hr.employee')
        hr_job_obj=self.pool.get('hr.job')
        company_obj = self.pool.get('res.company')
        res_partner_obj=self.pool.get('res.partner')
        hr_department_obj=self.pool.get('hr.department')
        hr_contract_obj=self.pool.get('hr.contract')
        data = self.browse(cr,uid,ids)[0]
        company_id = data.company_id.id
        import_file = data.import_file
        import_filename = data.name

        err_log = ''
        header_line = False

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

            if not ln or ln and ln[0] and ln[0][0] in ['', '#']:
                continue
            
            # process header line
            if not header_line:
                if ln[0].strip().lower() not in header_fields:
                    raise orm.except_orm(_('Error :'), _("Error while processing the header line %s. \n\nPlease check your EXCEL separator as well as the column header fields") %ln)
                else:
                    header_line = True
                    name_i = gender_i = marital_i = identification_id_i = mobile_phone_i = work_phone_i = work_email_i = birthday_i= father_name_i = fingerprint_id_i = job_i = department_i = address_home_i = blood_group_i = company_i = birth_place_i = birthday_month_i = None
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
                        if header_field not in header_fields:
                            err_log += '\n' + _("Invalid Excel File, Header Field '%s' is not supported !") %ln[i]
                        # required header fields : account, debit, credit
                        
                        elif header_field == 'name':
                            name_i = i
                        elif header_field == 'gender':
                            gender_i = i
                        elif header_field == 'marital':
                            marital_i = i
                        elif header_field == 'identification_id':
                            identification_id_i = i
                        elif header_field == 'mobile_phone':
                            mobile_phone_i = i
                        elif header_field == 'work_phone':
                            work_phone_i = i
                        elif header_field == 'work_email':
                            work_email_i = i
                        elif header_field == 'birthday':
                            birthday_i = i
                        elif header_field == 'father_name':
                            father_name_i = i
                        elif header_field == 'fingerprint_id':
                            fingerprint_id_i = i
                        elif header_field == 'job':
                            job_i = i
                        elif header_field == 'department':
                            department_i = i
                        elif header_field == 'address_home':
                            address_home_i = i
                        elif header_field == 'blood_group':
                            blood_group_i = i
                        elif header_field == 'company':
                            company_i = i    
                        elif header_field == 'birthday_month':
                            birthday_month_i = i
                        elif header_field == 'birth_place':
                            birth_place_i =i
                        
                        
                                               
                    for f in [(birthday_month_i,'birthday_month'),(name_i,'name'),(gender_i,'gender'),(marital_i,'marital'),(identification_id_i,'identification_id'),(mobile_phone_i,'mobile_phone'),(work_phone_i,'work_phone'),(work_email_i,'work_email'),(birthday_i,'birthday'),(father_name_i,'father_name'),(fingerprint_id_i,'fingerprint_id'),(job_i,'job_id'),(department_i,'department_id'),(address_home_i,'address_home_id'),(blood_group_i,'blood_group'),(company_i,'company_id'),(birth_place_i,'birth_place')]:
                        if not isinstance(f[0],int):
                            err_log += '\n'+ _("Invalid CSV file, Header '%s' is missing !") % f[1]
                        
                #process data lines   
            else:
                if ln and ln[0] and ln[0][0] not in ['#','']:
                    
                    import_vals = {}
                    
                    import_vals['name'] =  ln[name_i]
                    import_vals['gender'] = ln[gender_i]
                    import_vals['marital'] = ln[marital_i]
                    import_vals['identification_id'] = ln[identification_id_i]
                    import_vals['mobile_phone'] = ln[mobile_phone_i]
                    import_vals['work_phone'] = ln[work_phone_i]
                    import_vals['work_email'] = ln[work_email_i]
                    import_vals['birthday'] = ln[birthday_i]
                    import_vals['father_name']  = ln[father_name_i]
                    import_vals['fingerprint_id'] = ln[fingerprint_id_i]
                    import_vals['job'] = ln[job_i]
                    import_vals['department'] = ln[department_i]
                    import_vals['address_home'] = ln[address_home_i]
                    import_vals['blood_group']  = ln[blood_group_i]
                    import_vals['company'] = ln[company_i]
                    import_vals['birthday_month'] = ln[birthday_month_i]
                    import_vals['birth_place'] = ln[birth_place_i]
                    
                   
                    amls.append(import_vals)
       
        if err_log:
            self.write(cr, uid, ids[0], {'note': err_log})
            self.write(cr, uid, ids[0], {'state': 'failed'})
        else:
            for aml in amls:
                company_id = dept_id = address_name = job_id= time_format = None
                job_name = aml['job']
                company_name=aml['company']
                dept_name = aml['department']
                address = aml['address_home']
                emp_name=aml['name']
                birthday = aml['birthday']
                value={}
                        
                if emp_name:
                    address_id=res_partner_obj.search(cr,uid,[('name','=',emp_name)])
                    if not address_id:
                        address_value = {
                                     'name':emp_name,
                                     'street':address,
                                     'customer':False,
                                     'supplier':False
                                     }
                        address_ids = res_partner_obj.create(cr,uid,address_value, context)
                    else:
                        address_ids = address_id[0]
                print 'address',address_ids        

                if job_name:
                    job_ids= hr_job_obj.search(cr,uid,[('name','=',job_name)])
                    if not job_ids:
                        job_value = {
                                     'name':job_name,
                                     
                                     }
                        job_id = hr_job_obj.create(cr,uid,job_value,context)
                    else:
                        job_id= job_ids[0]
                print 'job_id ',job_id        
                        
                if dept_name:
                    dept_ids=company_obj.search(cr,uid,[('name','=',dept_name)])
                    if not dept_ids:
                        dept_value = {
                                     'name':dept_name ,
                                     }
                        dept_id = hr_department_obj.create(cr,uid,dept_value, context)
                    else:
                        dept_id = dept_ids[0]
                print 'dept',dept_id
                if birthday:
                    data_time = float(birthday)
                    result= xlrd.xldate.xldate_as_tuple(data_time,0)
                    a= str(result[1])+'/'+str(result[2])+'/'+str(result[0])+' '+str(result[3])+':'+str(result[4])+':'+str(result[5])
            
                    date_data = datetime.strptime(a, '%m/%d/%Y %H:%M:%S')
     

                if company_name:
                    company_ids=company_obj.search(cr,uid,[('name','=',company_name)])
                    if not company_ids:
                        com_value = {
                                     'name':company_name,
                                    # 'parent_id':company_id                                                                       
                                 
                          }
                        
                        company_name = company_obj.create(cr,uid,com_value, context)
                    else:
                        company_name = company_ids[0]
                    print 'company name',company_name
                    value={   'name':aml['name'],
                              'birthday_month':aml['birthday_month'].title()}
                   
                if aml['company']:
                    company=res_partner_obj.search(cr,uid,[('name','=',aml['company'])])   
                    if not company:
                        com_val={
                                 'name':aml['company'],
                                 'employee':False,
                                 'active':True,
                                 'display_name':aml['company'],
                                 'is_company':True}   
                        com_id=res_partner_obj.create(cr,uid,com_val,context)
                    else:
                        com_id=company[0]  
                    
                    value['company_id'] = company_name
                    value['job_id'] = job_id
                    value['department_id']=dept_id
                    value['address_home_id']=address_ids
                    value['birthday']=date_data.date()
                    value['gender']=aml['gender']
                    value['marital']=aml['marital']
                    value['identification_id']=aml['identification_id']
                    value['mobile_phone']=aml['mobile_phone']
                    value['work_email']=aml['work_email']
                    value['work_phone']=aml['work_phone']
                    value['father_name']=aml['father_name']
                    value['blood_group']=aml['blood_group']
                    value['fingerprint_id']=int(aml['fingerprint_id'])
                    value['place_of_birth']=aml['birth_place']
                    value['birthday_month']=aml['birthday_month']
                    value['address_id']= com_id
                    print 'time_format',value['birthday']   
                    
                employee_ids =  hr_employee_obj.search(cr,uid,[('name','=',aml['name']),
                                                               ('company_id','=',company_name),
                                                               ('department_id','=',dept_id),
                                                               ('job_id','=',job_id),
                                                               ('address_home_id','=',address_ids),
                                                             
                                                                  ]) 
                if not employee_ids:  
                    hr_employee_obj.create(cr,uid,value ,context=context)
                else:    
                    hr_employee_obj.write(cr,uid,employee_ids[0],value)  
            self.write(cr, uid, ids[0], {'state': 'completed'})
        print amls
