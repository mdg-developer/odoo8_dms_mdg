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
_logger = logging.getLogger(__name__)
header_fields = ['name_related', 'bank_account_id','gender', 'marital', 'identification_id', 'mobile_phone', 'work_phone',
    'work_email', 'birthday', 'father_name','fingerprint_id','department_id','permanent_date'
   , 'job_id','address_home_id','joining_date','permanent_salary','temporary_salary','education','other_qualification','working_experience','status',
   'bus_stop','section','nrc_prefix','nrc_number']

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

            if not ln or ln and ln[0] and ln[0][0] in ['', '#']:
                continue
            
            # process header line
            if not header_line:
                if ln[0].strip().lower() not in header_fields:
                    raise orm.except_orm(_('Error :'), _("Error while processing the header line %s. \n\nPlease check your Excel separator as well as the column header fields") %ln)
                else:
                    header_line = True
                    status_i =permanent_date_i = permanent_salary_i = temporary_salary_i =name_related_i = gender_i = marital_i = identification_id_i = mobile_phone_i = work_phone_i = work_email_i = birthday_i= father_name_i = fingerprint_id_i = job_id_i = department_id_i = address_home_id_i = joining_date_i = education_i = bank_account_id_i=other_qualification_i =working_experience_i=None
                    bus_stop_i = section_i = nrc_prefix_i = nrc_number_i = None
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
                        
                        elif header_field == 'name_related':
                            name_related_i = i
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
                        elif header_field == 'job_id':
                            job_id_i = i
                        elif header_field == 'department_id':
                            department_id_i = i
                        elif header_field == 'address_home_id':
                            address_home_id_i = i  
                        elif header_field == 'joining_date':
                            joining_date_i = i
                        elif header_field == 'bank_account_id':
                            bank_account_id_i = i          
                        elif header_field =='permanent_salary':
                            permanent_salary_i = i
                        elif header_field =='temporary_salary':
                            temporary_salary_i = i
                        elif header_field =='permanent_date':
                            permanent_date_i = i
                        elif header_field =='education':
                            education_i = i
                        elif header_field =='other_qualification':
                            other_qualification_i = i
                        elif header_field =='working_experience':
                            working_experience_i =i
                        elif header_field =='status':
                            status_i = i
                        elif header_field == 'bus_stop':    
                            bus_stop_i = i
                        elif header_field == "section":
                            section_i = i
                        elif header_field == "nrc_prefix":
                            nrc_prefix_i = i 
                        elif header_field == "nrc_number":
                            nrc_number_i = i         
                                               
                    for f in [(permanent_date_i,'permanent_date'),(permanent_salary_i,'permanent_salary'),(temporary_salary_i,'temporary_salary_i'),(bank_account_id_i,'bank_account_id'),(name_related_i,'name_related'),(gender_i,'gender'),(marital_i,'marital'),(nrc_prefix_i,'nrc_prefix'),(nrc_number_i,'nrc_number'),(mobile_phone_i,'mobile_phone'),(work_phone_i,'work_phone'),(work_email_i,'work_email'),(birthday_i,'birthday'),(father_name_i,'father_name'),(fingerprint_id_i,'fingerprint_id'),(job_id_i,'job_id'),(department_id_i,'department_id'),(address_home_id_i,'address_home_id'),(joining_date_i,'joining_date'),(education_i,'education'),(other_qualification_i,'other_qualification'),(working_experience_i,'working_experience'),(status_i,'status')]:
                        if not isinstance(f[0],int):
                            err_log += '\n'+ _("Invalid Excel file, Header '%s' is missing !") % f[1]
                        
                #process data lines   
            else:
                if ln and ln[0] and ln[0][0] not in ['#','']:
                    
                    import_vals = {}
                    
                    import_vals['name_related'] =  ln[name_related_i].strip()
                    import_vals['gender'] = ln[gender_i].strip()
                    import_vals['marital'] = ln[marital_i].strip()
                    #import_vals['identification_id'] = ln[identification_id_i].strip()
                    import_vals['mobile_phone'] = ln[mobile_phone_i]
                    import_vals['work_phone'] = ln[work_phone_i]
                    import_vals['work_email'] = ln[work_email_i].strip()
                    import_vals['birthday'] = ln[birthday_i]
                    import_vals['father_name']  = ln[father_name_i].strip()
                    import_vals['fingerprint_id'] = ln[fingerprint_id_i]
                    import_vals['job_id'] = ln[job_id_i].strip()
                    import_vals['department_id'] = ln[department_id_i].strip()
                    import_vals['address_home_id'] = ln[address_home_id_i].strip()
                    import_vals['joining_date'] = ln[joining_date_i]
                    import_vals['permanent_salary'] = ln[permanent_salary_i]
                    import_vals['temporary_salary'] = ln[temporary_salary_i]
                    import_vals['permanent_date'] = ln[permanent_date_i]
                    import_vals['education'] =ln[education_i]
                    import_vals['bank_account_id'] = ln[bank_account_id_i].strip()

                    import_vals['other_qualification']=ln[other_qualification_i]
                    import_vals['working_experience'] = ln[working_experience_i]
                    import_vals['status']=ln[status_i]
                    import_vals['bus_stop']= ln[bus_stop_i]
                    import_vals['section'] = ln[section_i]
                    import_vals['nrc_prefix'] = ln[nrc_prefix_i]
                    import_vals['nrc_number'] = ln[nrc_number_i]
                    amls.append(import_vals)
       
        if err_log:
            self.write(cr, uid, ids[0], {'note': err_log})
            self.write(cr, uid, ids[0], {'state': 'error'})
        else:
            for aml in amls:
                salary_structure = education_id=education_ids=payroll_schedule = policy_group = working_template = job_name = dept_name = address_id = emp_id = None
                bus_stop = section = nrc_prefix = bus_stop_i = section_i = nrc_prefix_i = nrc_number_i = None 
                per_date = join_date =datetime.today()
                job_id_name = aml['job_id'].encode('utf-8')
                joining_date =aml['joining_date']
                dept = aml['department_id'].encode('utf-8')
                address = aml['address_home_id'].encode('utf-8')
                bank = aml['bank_account_id'].encode('utf-8')
                emp_name=aml['name_related'].encode('utf-8')
                education=aml['education'].encode('utf-8')
                status=aml['status']
                bus_stop = aml['bus_stop'].encode('utf-8')
                section = aml['section'].encode('utf-8')
                nrc_prefix = aml['nrc_prefix'].encode('utf-8')
                nrc_number = aml['nrc_number'].encode('utf-8')
                
                if aml['fingerprint_id']=='':
                    fingerprint_id=''
                else:
                    fingerprint_id=int(aml['fingerprint_id'])
                birthday=aml['birthday']
                permanent_salary=aml['permanent_salary']
                temporary_salary=aml['temporary_salary']
                permanent_date=aml['permanent_date']
                 
                cr.execute('select min(id) from hr_payroll_structure')
                salary_structure=cr.fetchall()[0][0]
                cr.execute('select min(id) from hr_payroll_period_schedule')
                payroll_schedule=cr.fetchall()[0][0]
                cr.execute('select min(id) from hr_policy_group')
                policy_group=cr.fetchall()[0][0]
                cr.execute('select min(id) from hr_schedule_template')
                working_template=cr.fetchall()[0][0]
                
                if education:
                    education_ids=hr_recuritment_obj.search(cr,uid,[('name','=',education)])
                    education_value={'name':education}
                    if not education_ids:
                        education_id =hr_recuritment_obj.create(cr,uid,education_value,context)
                    else:
                        hr_recuritment_obj.write(cr,uid,education_ids[0],education_value)
                        education_id=education_ids[0]
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
                        
                bank_ids = None        
                if bank:
                    
                    bank_id=res_partner_bank_obj.search(cr,uid,[('acc_number','=',bank)])
                    
                    if not bank_id:
                        bank_value = {
                                     'state':'bank',
                                     'acc_number':bank,
                                     }
                        bank_ids = res_partner_bank_obj.create(cr,uid,bank_value, context)
                    else:
                        bank_ids = bank_id[0]          
                if job_id_name:
                    job_id_names= hr_job_obj.search(cr,uid,[('name','=',job_id_name)])
                    job_value = {
                                     'name':job_id_name,
                                     'cla_amount':0.0,
                                     'day':0.0,
                                     's_allowance':0.0,
                                     's_wage':0.0,
                                     's_contribution':0.0,
                                     'wage':0.0,
                                     'contribution':0.0,
                                     'allowance':0.0
                                     
                                     }
                    if not job_id_names:
                        job_name = hr_job_obj.create(cr,uid,job_value,context)
                    else:
                        #no need to update job
                        #hr_job_obj.write(cr,uid,job_id_names[0],job_value)
                        job_name= job_id_names[0]
                        
                     
                if dept:
                    depts=hr_department_obj.search(cr,uid,[('name','=',dept)])
                    dept_value = {
                                     'name':dept ,
                                     }
                    if not depts:
                        dept_name = hr_department_obj.create(cr,uid,dept_value, context)
                    else:
                        hr_department_obj.write(cr,uid,depts[0],dept_value)
                        dept_name = depts[0]
                        
                    value={   'name':emp_name,
                              'company_id':company_id,
                                'job_id':job_name}
                if section:
                    sections = hr_section_obj.search(cr,uid,[('name','=',section)])
                    section_value = {
                                     'name':section,
                                     'department_id':dept_name,
                                     }
                    if not sections:
                        section_name = hr_section_obj.create(cr,uid,section_value,context)
                    else:
                        hr_section_obj.write(cr,uid,sections[0],section_value)
                        section_name = sections[0]
                if nrc_prefix:
                    nrc_prefixs = hr_nrc_prefix_obj.search(cr,uid,[('name','=',nrc_prefix)])
                    nrc_prefixs_value = {
                                     'name':nrc_prefix,
                                     
                                     }
                    if not nrc_prefixs:
                        nrc_prefixs_name = hr_nrc_prefix_obj.create(cr,uid,nrc_prefixs_value,context)
                    else:
                        hr_nrc_prefix_obj.write(cr,uid,nrc_prefixs[0],nrc_prefixs_value)
                        nrc_prefixs_name = nrc_prefixs[0]
                                           
                if birthday:
                    try:
                        data_time = float(birthday)
                        result= xlrd.xldate.xldate_as_tuple(data_time,0)
                        a= str(result[1])+'/'+str(result[2])+'/'+str(result[0])+' '+str(result[3])+':'+str(result[4])+':'+str(result[5])
                
                        date_data = datetime.strptime(a, '%m/%d/%Y %H:%M:%S').date()
                    except Exception, e:
                        try:
                            str_date=str(birthday)+' 00:00:00'
                            date_data=datetime.strptime(str_date,'%m/%d/%Y %H:%M:%S').date()
                        except Exception, e:
                            try:
                                str_date=str(birthday)+' 00:00:00'
                                date_data=datetime.strptime(str_date,'%Y/%m/%d %H:%M:%S').date()
                            except Exception,e:
                                try:
                                    str_date=str(birthday)+' 00:00:00'
                                    date_data=datetime.strptime(str_date,'%d/%m/%Y %H:%M:%S').date()
                                except Exception,e:
                                    try:
                                        date_data=datetime.today().date()
                                    except Exception, e:
                                        raise orm.except_orm(_('Error :'), _("Error while processing Excel Columns. \n\nPlease check your Birthday!"))
                    
                if joining_date:
                    try:
                        data_time = float(joining_date)
                        result= xlrd.xldate.xldate_as_tuple(data_time,0)
                        a= str(result[1])+'/'+str(result[2])+'/'+str(result[0])+' '+str(result[3])+':'+str(result[4])+':'+str(result[5])
                
                        join_date = datetime.strptime(a, '%m/%d/%Y %H:%M:%S').date()
                    except Exception, e:
                        try:
                            str_date=str(joining_date)+' 00:00:00'
                            join_date=datetime.strptime(str_date,'%m/%d/%Y %H:%M:%S').date()
                        except Exception, e:
                            try:
                                str_date=str(joining_date)+' 00:00:00'
                                join_date=datetime.strptime(str_date,'%Y/%m/%d %H:%M:%S').date()
                            except Exception,e:
                                try:
                                    str_date=str(joining_date)+' 00:00:00'
                                    join_date=datetime.strptime(str_date,'%d/%m/%Y %H:%M:%S').date()
                                except Exception, e:
                                    try:
                                        join_date=datetime.today().date()
                                    except Exception, e:
                                        raise orm.except_orm(_('Error :'), _("Error while processing Excel Columns. \n\nPlease check your Joining Date!"))  
                if permanent_date:
                    try:
                        data_time = float(permanent_date)
                        result= xlrd.xldate.xldate_as_tuple(data_time,0)
                        a= str(result[1])+'/'+str(result[2])+'/'+str(result[0])+' '+str(result[3])+':'+str(result[4])+':'+str(result[5])
                
                        per_date = datetime.strptime(a, '%m/%d/%Y %H:%M:%S').date()
                    except Exception, e:
                        try:
                            str_date=str(permanent_date)+' 00:00:00'
                            per_date=datetime.strptime(str_date,'%m/%d/%Y %H:%M:%S').date()
                        except Exception, e:
                            try:
                                str_date=str(permanent_date)+' 00:00:00'
                                per_date=datetime.strptime(str_date,'%Y/%m/%d %H:%M:%S').date()
                            except Exception,e:
                                try:
                                    str_date=str(permanent_date)+' 00:00:00'
                                    per_date=datetime.strptime(str_date,'%d/%m/%Y %H:%M:%S').date()
                                except Exception ,e:
                                    try:
                                        per_date=datetime.today().date()
                                    except Exception, e:
                                        raise orm.except_orm(_('Error :'), _("Error while processing Excel Columns. \n\nPlease check your Permanent Date!"))  
                if dept_name:value['department_id']=dept_name
                if address_ids:value['address_home_id']=address_ids
                if bank_ids is not None:
                    value['bank_account_id']=bank_ids
                value['gender']=aml['gender']
                value['marital']=aml['marital']
                #value['identification_id']=aml['identification_id']
                value['mobile_phone']=aml['mobile_phone']
                value['work_email']=aml['work_email']
                value['work_phone']=aml['work_phone']
                value['birthday']=date_data
                value['father_name']=aml['father_name']
                value['fingerprint_id']= fingerprint_id
                value['initial_employment_date']=per_date
                if education_id:value['education_id']=education_id
                value['working_exp']=aml['working_experience']
                value['other']=aml['other_qualification']
                value['bus_stop'] = bus_stop
                value['section_id'] = section_name
                value['nrc_prefix_id'] = nrc_prefixs_name
                value['nrc_number'] = nrc_number
                if status:value['status']=status    
                
                if fingerprint_id<>'':
                    employee_ids =  hr_employee_obj.search(cr,uid,[
                                                                   ('fingerprint_id','=',fingerprint_id)
                                                                 
                                                                      ]) 
                    print 'employee_ids',employee_ids
                    if not employee_ids and fingerprint_id<>'':  
                        emp_id = hr_employee_obj.create(cr,uid,value ,context=context)
                        print 'emp',emp_id
                    else:    
                        hr_employee_obj.write(cr,uid,employee_ids[0],value)  
                        emp_id=employee_ids[0]
                        salary_structure = payroll_schedule = policy_group = working_template
                    if emp_id and job_name:
                        contract_value={
                                           'name':emp_name,
                                           'employee_id':emp_id,
                                           'wage':temporary_salary,
                                           's_wage':permanent_salary,
                                           'contribution':0.0,
                                           'allowance':0.0,
                                           's_contribution':0.0,
                                           's_allowance':0.0,
                                           'struct_id':1,
                                           'department_id':dept_name,
                                           'job_id':job_name,
                                           'joining_date':join_date,
                                           'struct_id':salary_structure,
                                           'pps_id':payroll_schedule,
                                           'policy_group_id':policy_group,
                                           'schedule_template_id':working_template,
                                           'trial_date_start':join_date,
                                           'trial_date_end':per_date,
                                           'date_start':per_date}


                        contract_id = hr_contract_obj.search(cr,uid,[('employee_id','=',emp_id)])
                        if not contract_id:
                            
                            hr_contract_obj.create(cr,uid,contract_value,context=context)
                        else:
                            hr_contract_obj.write(cr,uid,contract_id[0],contract_value)
            self.write(cr, uid, ids[0], {'state': 'completed'})
        print amls

#Under class is for hr_contract