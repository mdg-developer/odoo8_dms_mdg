from openerp.osv import orm
from openerp.osv import fields, osv
import xlrd
import codecs
from xlrd import open_workbook
from openerp.tools.translate import _
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
import base64
import logging

_logger = logging.getLogger(__name__)
header_fields = ['Name','Passport No','Gender','Employee No','Father Name','Date of Birth', 'NRC No', 'Level', 'Department',
    'Position', 'Joining Date', 'Probition Completed Date','Education'
   , 'Nationality','Religion','Contact No','Address','Remarks','Salary']

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
        service_obj =self.pool.get('service.level')
        hr_employee_obj = self.pool.get('hr.employee')
        hr_job_obj=self.pool.get('hr.job')
        company_obj = self.pool.get('res.company')
        res_partner_obj=self.pool.get('res.partner')
        hr_department_obj=self.pool.get('hr.department')
        hr_contract_obj=self.pool.get('hr.contract')
        res_country = self.pool.get('res.country')
        data = self.browse(cr,uid,ids)[0]
        company_id = data.company_id.id
        import_file = data.import_file
#        hr_academic_obj=self.pool.get('hr.academic')
        cr.execute('select min(id) from resource_calendar')
        datas = cr.fetchall()
        if datas:
            working_id = datas[0]
        else:
            working_id = None

        #cr.execute('select min(id) from hr_payroll_structure')
        datass = cr.fetchall()
        if datass:
            struct_id = datass[0]
        else:
            struct_id = None
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
                if ln[0].strip() not in header_fields:
                    raise orm.except_orm(_('Error :'), _("Error while processing the header line %s. \n\nPlease check your Excel separator as well as the column header fields") %ln)
                else:
                    header_line = True
                    name_i = gender_i = employee_no_i = father_name_i = passport_i = date_of_birth_i = nrc_no_i = level_i = dept_i = position_i = joining_date_i = probition_date_i = education_i = nationality_i = religion_i = contact_i = address_i =remarks_i  = salary_i = None
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
                            err_log += '\n' + _("Invalid Excel File, Header Field '%s' is not supported !") %ln[i]
                        # required header fields : account, debit, credit
                        elif header_field == 'Name':
                            name_i = i
                        elif header_field == 'Gender':
                            gender_i = i
                        elif header_field == 'Employee No':
                            employee_no_i = i
                            
                        elif header_field == 'Father Name':
                            father_name_i = i
                        elif header_field == 'Date of Birth':
                            date_of_birth_i = i
                        elif header_field == 'Passport No':
                            passport_i = i
                        elif header_field == 'NRC No':
                            nrc_no_i = i
                        elif header_field == 'Level':
                            level_i = i
                        elif header_field == 'Department':
                            dept_i = i
                        elif header_field == 'Position':
                            position_i = i
                        elif header_field == 'Joining Date':
                            joining_date_i = i
                        elif header_field == 'Probition Completed Date':
                            probition_date_i = i
                        elif header_field == 'Education':
                            education_i = i
                        elif header_field == 'Nationality':
                            nationality_i = i  
                        elif header_field == 'Religion':
                            religion_i = i
                        elif header_field =='Contact No':
                            contact_i = i
                        elif header_field =='Address':
                            address_i = i
                        elif header_field =='Remarks':
                            remarks_i = i
                        elif header_field =='Salary':
                            salary_i = i
                            
                        
                        
                                          
                    for f in [(name_i,'Name') ,(gender_i,'Gender' ),( employee_no_i,'Employee No'),(passport_i,'Passport No'),(father_name_i,'Father Name'),(date_of_birth_i,'Date of Birth'),(nrc_no_i,'NRC No'),(level_i,'Level'),(dept_i,'Department'),(position_i,'Position'),(joining_date_i,'Joining Date'),(probition_date_i,'Probition Completed Date'),(education_i,'Education'),(nationality_i,'Nationality'),(religion_i,'Religion'),(contact_i,'Contact No'),(address_i,'Address'),(remarks_i,'Remarks'),(salary_i,'Salary')]:
                        if not isinstance(f[0],int):
                            err_log += '\n'+ _("Invalid Excel file, Header '%s' is missing !") % f[1]
                        
                #process data lines   
            else:
              
                if ln and ln[0] and ln[0][0] not in ['#','']:
                   
                    import_vals = {}
                    if isinstance(ln[name_i], int) or isinstance(ln[name_i], float):
                            import_vals['Name']   = ln[name_i]
                    else:
                            import_vals['Name']  = ln[name_i].strip()                                                                                                                                                                                                                           
                          
                    if ln[gender_i]==None:
                        import_vals['Gender'] = ''
                    else:
                        import_vals['Gender'] = ln[gender_i].strip().lower()
                        
                    if ln[employee_no_i]==None:
                        import_vals['Employee No'] = ''
                    else:
                        if isinstance(ln[employee_no_i], int) or isinstance(ln[employee_no_i], float):
                            import_vals['Employee No']  = ln[employee_no_i]
                        else:
                            import_vals['Employee No']  = ln[employee_no_i].strip()
            
                    if ln[father_name_i]==None:
                        import_vals['Father Name'] = ''
                    else:
                        if isinstance(ln[father_name_i], int) or isinstance(ln[father_name_i], float):
                            import_vals['Father Name'] = ln[father_name_i]
                        else:
                            import_vals['Father Name'] = ln[father_name_i].strip()

                    if ln[date_of_birth_i]==None:
                        import_vals['Date of Birth'] = ''
                    else:
                        import_vals['Date of Birth'] = ln[date_of_birth_i]
                        
                    if ln[nrc_no_i]==None:
                        import_vals['NRC No'] = ''
                    else:
                        if isinstance(ln[nrc_no_i], int) or isinstance(ln[nrc_no_i], float):
                            import_vals['NRC No'] = ln[nrc_no_i]
                        else:
                            import_vals['NRC No'] = ln[nrc_no_i].strip()
                      
                    if ln[level_i] == None:
                        import_vals['Level'] = ''
                    else:
                        import_vals['Level'] = ln[level_i]
                        
                    if ln[dept_i]== None:
                        import_vals['Department'] =''
                    else:
                        if isinstance(ln[dept_i], int) or isinstance(ln[dept_i], float):
                            import_vals['Department'] = ln[dept_i]
                        else:
                            import_vals['Department']= ln[dept_i].strip()
                      
                    if ln[position_i]  == None:
                        import_vals['Position']  = ''
                    else:
                        if isinstance(ln[position_i], int) or isinstance(ln[position_i], float):
                            import_vals['Position']  = ln[position_i]
                        else:
                            import_vals['Position'] = ln[position_i].strip()
                        
                    if ln[joining_date_i] == None:
                        import_vals['Joining Date'] = ''
                    else:
                        import_vals['Joining Date'] = ln[joining_date_i]
                        
                    if ln[probition_date_i] == None:
                        import_vals['Probition Completed Date'] =''
                    else:
                        import_vals['Probition Completed Date'] = ln[probition_date_i]
                        
                    if ln[education_i] ==None:
                        import_vals['Education'] =''
                    else:
                        import_vals['Education'] = ln[education_i].strip()
                        
                    if ln[nationality_i] ==None:
                        import_vals['Nationality'] = ''
                    else:
                        if isinstance(ln[nationality_i], int) or isinstance(ln[nationality_i], float):
                            import_vals['Nationality']  = ln[nationality_i]
                        else:
                            import_vals['Nationality']= ln[nationality_i].strip()
                     
                    if ln[religion_i] ==None:
                        import_vals['Religion'] = ''
                    else:
                        if isinstance(ln[religion_i], int) or isinstance(ln[religion_i], float):
                            import_vals['Religion']   = ln[religion_i]
                        else:
                            import_vals['Religion'] = ln[religion_i].strip()
                        
                    if ln[contact_i] == None:
                        import_vals['Contact No'] = ''
                    else:
                        import_vals['Contact No'] = ln[contact_i]
                    
                    if  ln[address_i] ==None:
                        import_vals['Address'] = ''
                    else:
                        import_vals['Address'] = ln[address_i]
                    if ln[remarks_i] == None:
                        import_vals['Remarks'] = ''
                    else:
                        import_vals['Remarks'] = ln[remarks_i].strip()
                        
                    if  ln[salary_i]==None:
                        import_vals['Salary'] = ''
                    else:
                        import_vals['Salary'] =ln[salary_i]
                    if ln[passport_i]==None:
                        import_vals['Passport No'] = ''
                    else:
                        if isinstance(ln[passport_i], int) or isinstance(ln[passport_i], float):
                            import_vals['Passport No']   = ln[passport_i]
                        else:
                            import_vals['Passport No'] = ln[passport_i].strip()
                       
                    amls.append(import_vals)
       
        if err_log:
            self.write(cr, uid, ids[0], {'note': err_log})
            self.write(cr, uid, ids[0], {'state': 'failed'})
        else:
            for aml in amls:
               
                con_id = name_id = gender_id = employee_no_id = father_name_id = date_of_birth_id = nrc_no_id = level_id = dept_id = position_id = joining_date = probition_date = education_id = nationality_id = religion = contact = address_id =remarks  = salary = None
                date_end = join_date =datetime.today().date()
                per_date = None
                probition_date = aml['Probition Completed Date']#float has no encoded
                position = aml['Position']
                joining_date =aml['Joining Date']
                dept = aml['Department']
                address = aml['Address']
                education=aml['Education']
                remarks=aml['Remarks'].strip()
                name = aml['Name']
                passport = aml['Passport No']
           #     employee_no = aml['Employee No'].encode('utf-8')
                father_name = aml['Father Name']
                date_of_birth = aml['Date of Birth']#float has no encoded
                nrc_no = aml['NRC No']
                level = aml['Level']#float has no encoded
                nationality = aml['Nationality']
                religion = aml['Religion']
                contact = aml['Contact No']
                address = aml['Address']
                salary = aml['Salary']#float has no encoded

                if nationality:
                    nationality_ids = res_country.search(cr,uid,[('name','=',nationality)],context=context)
                    if not nationality_ids:
                        nationality_id = None
                    else:
                        nationality_id = nationality_ids[0]
                if aml['Employee No']=='': # Like a fingerprint_idd
                    employee_no=''
                else:
                    employee_no=str(aml['Employee No']).strip()
                    employee_no = employee_no.replace('.0', '')
                

                if name:
                    address_ids=res_partner_obj.search(cr,uid,[('name','=',name)])
                    if not address_ids:
                        address_value = {
                                     'name':name,
                                     'street':address,
                                     'customer':False,
                                     'supplier':False
                                     }
                        address_id = res_partner_obj.create(cr,uid,address_value, context)
                    else:
                        address_id = address_ids[0]
                        
    
                if position:
                    position_ids= hr_job_obj.search(cr,uid,[('name','=',position)])
                    job_value = {
                                     'name':position
                                     
                                     }
                    if not position_ids:
                        position_id = hr_job_obj.create(cr,uid,job_value,context)
                    else:
                        #no need to update job
                        #hr_job_obj.write(cr,uid,job_id_names[0],job_value)
                        position_id= position_ids[0]
                        
                     
                if dept:
                    dept_ids=hr_department_obj.search(cr,uid,[('name','=',dept)])
                    dept_value = {
                                     'name':dept ,
                                     }
                    if not dept_ids:
                        dept_id = hr_department_obj.create(cr,uid,dept_value, context)
                    else:
                        hr_department_obj.write(cr,uid,dept_ids[0],dept_value)
                        dept_id = dept_ids[0]
                        
                    value={   'name':name,
                              'company_id':company_id,
                                'job_id':position_id}
                if date_of_birth:
                    try:
                        data_time = float(date_of_birth)
                        result= xlrd.xldate.xldate_as_tuple(data_time,0)
                        a= str(result[1])+'/'+str(result[2])+'/'+str(result[0])+' '+str(result[3])+':'+str(result[4])+':'+str(result[5])
                
                        date_data = datetime.strptime(a, '%m/%d/%Y %H:%M:%S').date()
                    except Exception, e:
                        try:
                            str_date=str(date_of_birth)+' 00:00:00'
                            date_data=datetime.strptime(str_date,'%m/%d/%Y %H:%M:%S').date()
                        except Exception, e:
                            try:
                                str_date=str(date_of_birth)+' 00:00:00'
                                date_data=datetime.strptime(str_date,'%Y/%m/%d %H:%M:%S').date()
                            except Exception,e:
                                try:
                                    str_date=str(date_of_birth)+' 00:00:00'
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
                if probition_date:
                    try:
                        data_time = float(probition_date)
                        result= xlrd.xldate.xldate_as_tuple(data_time,0)
                        a= str(result[1])+'/'+str(result[2])+'/'+str(result[0])+' '+str(result[3])+':'+str(result[4])+':'+str(result[5])
                
                        per_date = datetime.strptime(a, '%m/%d/%Y %H:%M:%S').date()
                    except Exception, e:
                        try:
                            str_date=str(probition_date)+' 00:00:00'
                            per_date=datetime.strptime(str_date,'%m/%d/%Y %H:%M:%S').date()
                        except Exception, e:
                            try:
                                str_date=str(probition_date)+' 00:00:00'
                                per_date=datetime.strptime(str_date,'%Y/%m/%d %H:%M:%S').date()
                            except Exception,e:
                                try:
                                    str_date=str(probition_date)+' 00:00:00'
                                    per_date=datetime.strptime(str_date,'%d/%m/%Y %H:%M:%S').date()
                                except Exception ,e:
                                    try:
                                        per_date=None
                                    except Exception, e:
                                        raise orm.except_orm(_('Error :'), _("Error while processing Excel Columns. \n\nPlease check your Permanent Date!"))  
                if join_date:
                    date_end = join_date+  relativedelta(months = 3)
                if per_date:
                    per_date  = per_date +timedelta(days=1)
                elif not per_date:
                    per_date = date_end + timedelta(days=1)
                if dept_id:value['department_id']=dept_id
                if address_id:value['address_home_id']=address_id
                if level:
                    try : 
                        level_ids = service_obj.search(cr,uid,[('level','=',int(level))])
                        if not level_ids:
                            level_id = service_obj.create(cr,uid,{'level':int(level),'name':int(level)},context=context)
                        else:
                            level_id =level_ids[0]
                    except Exception, e:
                        level_id=None
                        

                
                value['gender']=aml['Gender']
                value['passport_id'] = aml['Passport No']
                value['identification_id']=nrc_no
                value['birthday']=date_data
                value['fingerprint_id'] = employee_no
                value['father_name']=father_name
                value['country_id']=nationality_id
                try:
                    value['fingerprint_id'] = employee_no
                except Exception, e:
                   
                    break
            
                if remarks:
                    if remarks.lower()=='dismiss':
                        remarks = 'inactive'   
                    elif remarks=='':
                        remarks = 'active'#default
                    else:
                        remarks='active'#default     
                                 
                if employee_no=='':
                    continue
                else:
                    employee_ids =  hr_employee_obj.search(cr,uid,[
                                                                   ('fingerprint_id','=',employee_no)
                                                                 
                                                                      ]) 
                    if not employee_ids and employee_no<>'':  
                        emp_id = hr_employee_obj.create(cr,uid,value ,context=context)
                    else:    
                        hr_employee_obj.write(cr,uid,employee_ids[0],value)  
                        emp_id=employee_ids[0]
                    #after created the employee and then create education
#                    if emp_id:
#                        cr.execute('update hr_employee set status =%s  where id = %s',(remarks,emp_id,))

#
#                    if emp_id and education:
#
#                        edu = str(education).split(',')
#                        if edu:
#                            for val in edu:
#                                education_ids=hr_academic_obj.search(cr,uid,[('name','=',val),('employee_id','=',emp_id)])
#                                education_value={'name':val,'employee_id':emp_id}
#                                if not education_ids:
#                                    hr_academic_obj.create(cr,uid,education_value,context)
#                                else:
#                                    hr_academic_obj.write(cr,uid,education_ids[0],education_value)
                            
                    if emp_id and position_id and remarks!='inactive' :
                        contract_value={
                                           'name':name,
                                           'employee_id':emp_id,
                                           'wage':salary,
                                           's_wage':salary,
                                           'contribution':0.0,
                                           'allowance':0.0,
                                           's_contribution':0.0,
                                           's_allowance':0.0,
                                           'struct_id':struct_id,
                                           'department_id':dept_id,
                                           'job_id':position_id,
                                           'joining_date':join_date,
                                           'trial_date_start':join_date,
                                           'trial_date_end':date_end,
                                           'date_start':per_date,
                                           'level_id':level_id,
                                           'working_hours':working_id}
                        contract_ids = hr_contract_obj.search(cr,uid,[('employee_id','=',emp_id)])
                        if not contract_ids:
                            
                            hr_contract_obj.create(cr,uid,contract_value,context=context)
                        else:
                            hr_contract_obj.write(cr,uid,contract_ids[0],contract_value)
                    elif emp_id and position_id and remarks=='inactive' :
                        #print 'inactive',remarks
                        contract_value={
                                           'name':name,
                                           'employee_id':emp_id,
                                           'wage':salary,
                                           's_wage':salary,
                                           'contribution':0.0,
                                           'allowance':0.0,
                                           's_contribution':0.0,
                                           's_allowance':0.0,
                                           'struct_id':struct_id,
                                           'department_id':dept_id,
                                           'job_id':position_id,
                                           'joining_date':join_date,
                                           'trial_date_start':join_date,
                                           'trial_date_end':date_end,
                                           'date_start':per_date,
                                           'level_id':level_id,
                                           'working_hours':working_id}

                        contract_ids = hr_contract_obj.search(cr,uid,[('employee_id','=',emp_id)])
                        if not contract_ids:
                            
                            con_id = hr_contract_obj.create(cr,uid,contract_value,context=context)
                        else:
                            con_id = contract_ids[0]
                            hr_contract_obj.write(cr,uid,contract_ids[0],contract_value)
                        if con_id:
                            cr.execute('update hr_contract set state=%s where employee_id =%s',('done',emp_id,))
                self.write(cr, uid, ids[0], {'state': 'completed'})
        print amls

#Under class is for hr_contract