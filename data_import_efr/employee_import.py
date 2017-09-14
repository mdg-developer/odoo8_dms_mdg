from openerp.osv import orm
from openerp.osv import fields, osv
import xlrd
from xlrd import open_workbook
from openerp.tools.translate import _
from datetime import datetime
import base64
import logging
_logger = logging.getLogger(__name__)
#'identification_id',
header_fields = ['birthday_month','name', 'gender', 'marital',  'mobile_phone', 'work_phone',
    'work_email', 'birthday', 'father_name','fingerprint_id','department'
   , 'job','address_home','blood_group','company','birth_place','joining_date','permanent_date',
    'bus_stop','section','nrc_prefix','nrc_number','labour_card','contract_wage']

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
              'message':fields.char('Total Number Of Rows',readonly=True)
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
    
    _constraints = [(_check_file_ext,"Please import Excel file!",['import_fname'])]
    
    def import_data(self, cr, uid, ids, context=None):
        hr_employee_obj = self.pool.get('hr.employee')
        hr_job_obj=self.pool.get('hr.job')
        company_obj = self.pool.get('res.company')
        res_partner_obj=self.pool.get('res.partner')
        hr_department_obj=self.pool.get('hr.department')
        hr_section_obj=self.pool.get('hr.section')
        hr_nrc_prefix_obj=self.pool.get('hr.nrc.prefix')
        data = self.browse(cr,uid,ids)[0]
        import_file = data.import_file
        company_id=data.company_id
        count=0
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
            try:
                if not ln or ln and ln[0] and ln[0][0] in ['', '#']:
                    continue
                
                # process header line
                if not header_line:
                    if ln[0].strip().lower() not in header_fields:
                        raise orm.except_orm(_('Error :'), _("Error while processing the header line %s. \n\nPlease check your Excel separator as well as the column header fields") %ln)
                    else:
                        header_line = True
                        joining_date_i = permanent_date_i = birthday_month_i = name_i = gender_i = marital_i = identification_id_i = mobile_phone_i = work_phone_i = work_email_i = birthday_i= father_name_i = fingerprint_id_i = job_i = department_i = address_home_i = blood_group_i = company_i = birth_place_i = labour_card_i = contract_wage_i = None
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
                                err_log += '\n' + _("Invalid CSV File, Header Field '%s' is not supported !") %ln[i]
                            # required header fields : account, debit, credit
                            
                            elif header_field == 'name':
                                name_i = i
                            elif header_field == 'gender':
                                gender_i = i
                            elif header_field == 'marital':
                                marital_i = i
#                             elif header_field == 'identification_id':
#                                 identification_id_i = i
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
                            elif header_field == 'birth_place':
                                birth_place_i = i
                            elif header_field == 'birthday_month':
                                birthday_month_i = i
                            elif header_field == 'joining_date':
                                joining_date_i = i
                            elif header_field == 'permanent_date':
                                permanent_date_i = i                            
                            elif header_field == 'bus_stop':    
                                bus_stop_i = i
                            elif header_field == "section":
                                section_i = i
                            elif header_field == "nrc_prefix":
                                nrc_prefix_i = i 
                            elif header_field == "nrc_number":
                                nrc_number_i = i
                            elif header_field == 'labour_card':
                                labour_card_i = i
                            elif header_field == 'contract_wage':
                                contract_wage_i = i    
                        #(identification_id_i,'identification_id'),                           
                        for f in [(joining_date_i,'joining_date'),(permanent_date_i,'permanent_date'),(birthday_month_i,'birthday_month'),(name_i,'name'),(gender_i,'gender'),(marital_i,'marital'),(mobile_phone_i,'mobile_phone'),(work_phone_i,'work_phone'),(work_email_i,'work_email'),(birthday_i,'birthday'),(father_name_i,'father_name'),(fingerprint_id_i,'fingerprint_id'),(job_i,'job'),(department_i,'department'),(address_home_i,'address_home'),(blood_group_i,'blood_group'),(company_i,'company'),(birth_place_i,'birth_place'),(labour_card_i,'labour_card'),(contract_wage_i,'contract_wage')]:
                            if not isinstance(f[0],int):
                                err_log += '\n'+ _("Invalid CSV file, Header '%s' is missing !") % f[1]
                            
                    #process data lines   
                else:
                    if ln and ln[0] and ln[0][0] not in ['#','']:
                        
                        import_vals = {}
                        try:
                            print 'ln[name_i]>>',ln[name_i]
                            import_vals['name'] =  ln[name_i]
                            import_vals['gender'] = ln[gender_i]
                            import_vals['marital'] = ln[marital_i]
                            #import_vals['identification_id'] = ln[identification_id_i]
                            import_vals['mobile_phone'] = ln[mobile_phone_i]
                            import_vals['work_phone'] = ln[work_phone_i]
                            import_vals['work_email'] = ln[work_email_i]
                            import_vals['birthday'] = ln[birthday_i]
                            import_vals['father_name']  = ln[father_name_i]
                            if ln[fingerprint_id_i]:
                                import_vals['fingerprint_id'] = str(int(ln[fingerprint_id_i])).strip()
                                print 'ln[fingerprint_id]',ln[fingerprint_id_i]
                                print 'this is fingerprint id contain'
                            else:
                                import_vals['fingerprint_id']=''
                                print 'no fingerprint id '
#                            import_vals['fingerprint_id']=ln['fingerprint_id_i'].strip()
                            import_vals['job'] = ln[job_i]
                            import_vals['department'] = ln[department_i]
                            import_vals['address_home'] = ln[address_home_i]
                            import_vals['blood_group']  = ln[blood_group_i]
                            import_vals['company'] = ln[company_i]
                            import_vals['birth_place'] = ln[birth_place_i]
                            import_vals['birthday_month'] = ln[birthday_month_i]
                            import_vals['joining_date'] = ln[joining_date_i]
                            import_vals['permanent_date'] = ln[permanent_date_i]
                            import_vals['bus_stop']= ln[bus_stop_i]
                            import_vals['section'] = ln[section_i]
                            import_vals['nrc_prefix'] = ln[nrc_prefix_i]
                            import_vals['nrc_number'] = ln[nrc_number_i]
                            import_vals['labour_card'] = ln[labour_card_i]
                            import_vals['contract_wage'] = ln[contract_wage_i]
                        except Exception, e:
                            raise orm.except_orm(_('Error :'), _("Error while Checking the Excel Data %s")%e)
                       
                        amls.append(import_vals)
            except Exception , e:
                raise orm.except_orm(_('Error :'),_("Error while Checking the Excel Format Cell %s")%e)
                    
        if err_log:
            self.write(cr, uid, ids[0], {'note': err_log})
            self.write(cr, uid, ids[0], {'state': 'failed'})
        else:
            for aml in amls:
                try:
                    company_name_id = job_name_id = dept_name_id = None
                    err_log =''
                    value={}
                    date_data1=datedata2=date_data3=None
                    job_name = aml['job']
                    company_name=aml['company']
                    dept = aml['department']
                    address = aml['address_home']
                    emp_name=aml['name']
                    joining_date = aml['joining_date']
                    permanent_date = aml['permanent_date']
                    birthday=aml['birthday']
                    work_phone =str(aml['work_phone'])
                    fingerprint_id=aml['fingerprint_id']
                    bus_stop = aml['bus_stop'].encode('utf-8')
                    section = aml['section'].encode('utf-8')
                    nrc_prefix = aml['nrc_prefix'].encode('utf-8')
                    nrc_number = aml['nrc_number'].encode('utf-8')
                    total='Total rows :'
                    if company_name:
                        company_names=company_obj.search(cr,uid,[('name','=',company_name)])
                        com_value = {
                                     'name':company_name,
                                     'parent_id':company_id                                                                       
                                 
                          }
                        
                        if not company_names:
                            company_name_id = company_obj.create(cr,uid,com_value, context)
                        else:
                            company_obj.write(cr,uid,company_names[0],com_value)
                            company_name_id = company_names[0]
                    if emp_name:
                        address_id=res_partner_obj.search(cr,uid,[('name','=',emp_name)])
                        address_value = {
                                     'name':emp_name,
                                     'street':address,
                                     'customer':False,
                                     'supplier':False
                                     }
                        if not address_id:
                            address_ids = res_partner_obj.create(cr,uid,address_value, context)
                        else:
                            res_partner_obj.write(cr,uid,address_id[0],address_value)
                            address_ids = address_id[0]
                    if job_name:
                        job_names= hr_job_obj.search(cr,uid,[('name','=',job_name)])
                        job_value = {
                                     'name':job_name,'company_id':company_name_id,
                                     
                                     }
                        if not job_names:
                            job_name_id = hr_job_obj.create(cr,uid,job_value,context)
                        else:
                            hr_job_obj.write(cr,uid,job_names[0],job_value)
                            job_name_id= job_names[0]
                    bus_stop_id = None        
                    if bus_stop:
                        bus_stop_obj = self.pool.get('hr.bus.stop')
                        bus_stops = bus_stop_obj.search(cr,uid,[('name','=',bus_stop)])
                        bus_value = {'name':bus_stop}
                        if not bus_stops:
                            bus_stop_id = bus_stop_obj.create(cr,uid,bus_value,context)
                        else:
                            bus_stop_obj.write(cr,uid,bus_stops[0],bus_value)
                            bus_stop_id = bus_stops[0]             
                    if dept:
                        depts=hr_department_obj.search(cr,uid,[('name','=',dept)])
                        dept_value = {
                                     'name':dept ,'company_id':company_name_id,
                                     }
                        if not depts:
                            dept_name_id = hr_department_obj.create(cr,uid,dept_value, context)
                        else:
                            hr_department_obj.write(cr,uid,depts[0],dept_value)
                            dept_name_id = depts[0]
                            
                    
                    if section:
                        sections = hr_section_obj.search(cr,uid,[('name','=',section)])
                        section_value = {
                                         'name':section,
                                         'department_id':dept_name_id,
                                         }
                        if not sections:
                            section_name = hr_section_obj.create(cr,uid,section_value,context)
                            value['section_id']= section_name
                        else:
                            hr_section_obj.write(cr,uid,sections[0],section_value)
                            section_name = sections[0]
                            value['section_id']= section_name
                            
                    if nrc_prefix:
                        nrc_prefixs = hr_nrc_prefix_obj.search(cr,uid,[('name','=',nrc_prefix)])
                        nrc_prefixs_value = {
                                         'name':nrc_prefix,
                                         
                                         }
                        if not nrc_prefixs:
                            nrc_prefixs_name = hr_nrc_prefix_obj.create(cr,uid,nrc_prefixs_value,context)
                            value['nrc_prefix_id']= nrc_prefixs_name
                            value['nrc_number']= nrc_number
                        else:
                            hr_nrc_prefix_obj.write(cr,uid,nrc_prefixs[0],nrc_prefixs_value)
                            nrc_prefixs_name = nrc_prefixs[0]        
                            
                            
                    if birthday:
                        try:
                            data_time = float(birthday)
                            result= xlrd.xldate.xldate_as_tuple(data_time,0)
                            a= str(result[1])+'/'+str(result[2])+'/'+str(result[0])+' '+str(result[3])+':'+str(result[4])+':'+str(result[5])
                    
                            date_data1 = datetime.strptime(a, '%m/%d/%Y %H:%M:%S')
                        except Exception, e:
                            try:
                                date_data1=datetime.today()
                            except Exception, e:
                                raise orm.except_orm(_('Error :'), _("Error while processing Excel Columns. \n\nPlease check your Birthday!"))

                    if joining_date:
                        try:
                            data_time = float(joining_date)
                            result= xlrd.xldate.xldate_as_tuple(data_time,0)
                            a= str(result[1])+'/'+str(result[2])+'/'+str(result[0])+' '+str(result[3])+':'+str(result[4])+':'+str(result[5])
                    
                            join_date = datetime.strptime(a, '%m/%d/%Y %H:%M:%S')
                        except Exception, e:
                            try:
                                join_date=datetime.today()
                            except Exception, e:
                                raise orm.except_orm(_('Error :'), _("Error while processing Excel Columns. \n\nPlease check your Joining Date!"))
                    permanent = None        
                    if permanent_date:
                        try:
                            data_time = float(permanent_date)
                            result= xlrd.xldate.xldate_as_tuple(data_time,0)
                            a= str(result[1])+'/'+str(result[2])+'/'+str(result[0])+' '+str(result[3])+':'+str(result[4])+':'+str(result[5])
                    
                            permanent = datetime.strptime(a, '%m/%d/%Y %H:%M:%S')
                        except Exception, e:
                            try:
                                permanent=datetime.today()
                            except Exception, e:
                                raise orm.except_orm(_('Error :'), _("Error while processing Excel Columns. \n\nPlease check your permanent date!"))
                    value={'name':aml['name'],
                              'birthday_month':aml['birthday_month']}
                    if date_data1:                       
                        value['birthday']=date_data1

                    if company_name:value['company_id'] = company_name_id
                    if job_name_id:value['job_id'] = job_name_id
                    if dept_name_id:value['department_id']=dept_name_id
                    if address_ids:value['address_home_id']=address_ids
                    if nrc_number:
                        value['nrc_number']= nrc_number
                    if nrc_prefixs_name:
                        value['nrc_prefix_id']= nrc_prefixs_name
                    if section_name:
                        value['section_id']= section_name 
                    if bus_stop_id:
                        value['bus_stop_id']= bus_stop_id       
                    value['gender']=aml['gender']
                    value['marital']=aml['marital']
                    #value['identification_id']=aml['identification_id']
                    value['mobile_phone']=aml['mobile_phone']
                    value['work_email']=aml['work_email']
                    value['work_phone']=work_phone
                    value['father_name']=aml['father_name']
                    value['blood_group']=aml['blood_group']
                    value['labour_card']=aml['labour_card']
                    if len(fingerprint_id)>0:
                        value['fingerprint_id']=fingerprint_id
                   
                        employee_ids =  hr_employee_obj.search(cr,uid,[('fingerprint_id','=',fingerprint_id),
                                                                       ('company_id','=',company_name_id)
                                                                     
                                                                          ]) 
                        if not employee_ids:
                            print 'value>>>',value  
                            emp_id = hr_employee_obj.create(cr,uid,value ,context=context)
                            count+=1
                        else:    
                            hr_employee_obj.write(cr,uid,employee_ids[0],value) 
                            emp_id = employee_ids[0]
#                            count+=1
                    else:
                        no_fingerprint="There NO FINGERPRINT ID !"
                        raise orm.except_orm(_('Error :'),_("Error while Adding the value in Fingerprint id %s")%no_fingerprint)
                        
                except Exception,e: 
                    raise orm.except_orm(_('Error :'), _("Error while Adding the value in Employee %s") %e)
                    err_log+=' \n'+value+' '
                    
                try:
                    if emp_id:
                        contract_value={}
                        type_ids = self.pool.get('hr.contract.type').search(cr,uid,[('name','=','Employee')])
                        if not type_ids:
                            type_id = self.pool.get('hr.contract.type').create(cr,uid,{'name':'Employee'},context)
                        else:
                            type_id=type_ids[0]
                        struct_ids =self.pool.get('hr.payroll.structure').search(cr,uid,[('name','=','Base for new structures')])
                        if not struct_ids:
                            struct_id = self.pool.get('hr.payroll.structure').create(cr,uid,{'name':'Base for new structures','code':'BASE','company_id':company_name_id},context)
                        else:
                            struct_id=struct_ids[0]
                        contract_value={'name':emp_name,
                                        'employee_id':emp_id,
                                        'type_id':type_id,
                                        'job_id':job_name_id,
                                        'struct_id':struct_id,
                                        'wage':aml['contract_wage']
                                       
                                        } 
                        if join_date:
                            contract_value['joining_date']=join_date
                            contract_value['trial_date_start']=join_date
                        if permanent:
                            contract_value['date_start'] = permanent
                        
                            

                        con_ids = self.pool.get('hr.contract').search(cr,uid,[('name','=',emp_name),('employee_id','=',emp_id)])
                        if not con_ids:
                            self.pool.get('hr.contract').create(cr,uid,contract_value,context)
                        else:
                            print 'Contract already exist!'
                except Exception, e:
                    raise orm.except_orm(_('Error :'),_("Error while Adding the value in Contract%s")%e)
            self.write(cr, uid, ids[0], {'state': 'completed','log':err_log})
        self.write(cr,uid,ids[0],{'message':count})    
        print amls

#Under class is for hr_contract
