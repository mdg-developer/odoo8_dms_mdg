# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Noviat nv/sa (www.noviat.com). All rights reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import orm
from openerp.osv import fields, osv
from xlrd import open_workbook
from openerp.tools.translate import _
from datetime import datetime
import base64, StringIO, csv
import base64
import logging

_logger = logging.getLogger(__name__)
header_fields = ['FR Name','Sequence','Type','Parent A/C','Sign','Financial Report Style','COA Name','Account Code','Display Type','Analytic Code']

class account_report(osv.osv):
    _name = 'data_import.account'
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
            if '.csv' in import_file.import_fname:return True
            else: return False
        return True
    
    _constraints = [(_check_file_ext,"Please import Excel file!",['import_fname'])]
    
    def import_data(self, cr, uid, ids, context=None):
        acc_financial_obj=self.pool.get('account.financial.report')
        account_account_obj=self.pool.get('account.account')
        account_type_obj=self.pool.get('account.account.type')
        #for analytic account code
        analytic_obj=self.pool.get('account.analytic.account')
        cr.execute('delete from account_account_financial_report')
        cr.execute('delete from account_account_financial_report_type')
        data = self.browse(cr,uid,ids)[0]
        import_file = data.import_file
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
                if ln[0].strip() not in header_fields:
                    raise orm.except_orm(_('Error :'), _("Error while processing the header line %s. \n\nPlease check your Excel separator as well as the column header fields") %ln)
                else:
                    header_line = True
                    fr_name_i = sequence_i = type_i = parent_ac_i =sign_i = report_style_i = coa_name_i = account_code_i = display_code_i = analytic_code_i = None
                    column_cnt = 0
                    i=0
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
                        elif header_field == 'FR Name':
                            fr_name_i = i
                        elif header_field == 'Sequence':
                            sequence_i = i
                        elif header_field == 'Type':
                            type_i = i
                        elif header_field == 'Parent A/C':
                            parent_ac_i = i
                        elif header_field == 'Sign':
                            sign_i = i
                        elif header_field == 'Financial Report Style':
                            report_style_i = i            
                        elif header_field =='COA Name':
                            coa_name_i = i
                        elif header_field =='Account Code':
                            account_code_i = i
                        elif header_field =='Display Type':
                            display_type_i = i
                        elif header_field =='Analytic Code':
                            analytic_code_i = i
                                      
                    for f in [(analytic_code_i,'Analytic Code'),(display_type_i,'Display Type'),(fr_name_i,'FR Name'),(sequence_i,'Sequence'),(type_i,'Type'),(sign_i,'Sign'),(parent_ac_i,'Parent A/C'),(report_style_i ,'Financial Report Style'),(coa_name_i,'COA Name'),(account_code_i,'Account Code')]:
                        if not isinstance(f[0],int):
                            err_log += '\n'+ _("Invalid Excel file, Header '%s' is missing !") % f[1]
                        
                #process data lines   
            else:
                if ln and ln[0] and ln[0][0] not in ['#','']:
                    import_vals = {}
                    import_vals['FR Name'] =  ln[fr_name_i]
                    import_vals['Sequence'] =  ln[sequence_i] 
                    import_vals['Type'] =  ln[type_i]
                    import_vals['Parent A/C'] =  ln[parent_ac_i]
                    import_vals['Sign'] = ln[sign_i]
                    import_vals['Financial Report Style'] =  ln[report_style_i]   
                    import_vals['COA Name'] = ln[coa_name_i]     
                    import_vals['Account Code'] = ln[account_code_i]  
                    import_vals['Display Type'] = ln[display_type_i]           
                    import_vals['Analytic Code'] = ln[analytic_code_i]             
                    amls.append(import_vals)
                  
        if err_log:
            self.write(cr, uid, ids[0], {'note': err_log})
            self.write(cr, uid, ids[0], {'state': 'failed'})
        else:
            for aml in amls:
                try:
                    fr_name = sequence = type = coa_name =parent = sign = report_style = account_code = display_type = analytic_code = None
                    count=acc_count =0
                    #some font type is Unicode so I use UTF-8 encoding
                    if aml['FR Name']:
                        fr_name = str(aml['FR Name'].encode('utf-8'))
                        fr_name = fr_name.strip()
                    else:
                        fr_name = None
                        
                    if aml['Account Code']:
                        account_code = str(aml['Account Code'])
                        account_code =account_code.strip()
                    else:
                        account_code = None
                        
                    #I wish to change parent code to .title() but there some report names are same but all cap letter and also small letter. 
                    if aml['Parent A/C']:
                        parent = str(aml['Parent A/C'].encode('utf-8'))
                        parent = parent.strip()
                    else:
                        parent = None
                        
                    if aml['Type']:
                        type = str(aml['Type'].encode('utf-8'))
                        type = type.strip()
                        if type=='View':
                            type='sum'
                        elif type=='Accounts':
                            type='accounts'
                        elif type=='Report Value':
                            type='account_report'
                        elif type=='Account Type':
                            type='account_type'
                    else:
                        type = None
                        
                    if aml['Sequence']:
                        sequence = int(aml['Sequence'])
                    else:
                        sequence=None
                        
                    if aml['Financial Report Style']:
                        report_style =str(aml['Financial Report Style'])
                        report_style = report_style.strip()
                    else:
                        report_style = None
                    # no used COA Name in program    
                    if aml['COA Name']:
                        coa_name = str(aml['COA Name'].encode('utf-8'))
                        coa_name = coa_name.strip()
                    else:
                        coa_name = None
                    
                    if aml['Sign']:
                        sign = str(aml['Sign']).lower()
                        sign = sign.strip()
                    else:
                        sign = None
                   
                    #No Detail , Display with flat , Display with hierarchy
                    if aml['Display Type'] :
                        display_type = int(aml['Display Type'])
                    else:
                        dispaly_type = None     
                        
                    #Analytic Code
                    if aml['Analytic Code']:
                        analytic_code = str(aml['Analytic Code']).strip()    
                    else:
                        analytic_code = None
                        
                    #report with parent
                    if parent:
                        parent_id=acc_financial_obj.search(cr,uid,[('name','=',parent)])
                        
                        #parent is true but can't search in financial report
                        if not parent_id:
                            report_val={'name':fr_name,'sequence':sequence}
                            
                            #condition for style
                            if report_style=='automatic':
                                report_val['style_overwrite']=None
                            elif report_style=='title1':
                                report_val['style_overwrite']=1
                            elif report_style=='title2':
                                report_val['style_overwrite']=2
                            elif report_style=='title3':
                                report_val['style_overwrite']=3
                            elif report_style=='normal':
                                report_val['style_overwrite']=4
                            elif report_style=='italic':
                                report_val['style_overwrite']=5
                            elif report_style=='smallest':
                                report_val['style_overwrite']=6
                            else:
                                report_val['style_overwrite']=None
                                
                            #condition for sign
                            #reverse condition
                            if sign=='reverse':
                                report_val['sign']=-1
                            #preserve condition
                            elif sign=='preserve':
                                report_val['sign']=1
                            #null condition
                            else:
                                report_val['sign']=1
                               
                            #Report with Display Type
                            if display_type==1:
                                report_val['display_detail']='no_detail'
                            elif display_type==2:
                                report_val['display_detail'] = 'detail_flat'
                            elif display_type==3:
                                report_val['display_detail'] = 'detail_with_hierarchy'
                            else:
                                report_val['display_detail'] = 'no_detail'
                            
                            #analytic code
                            if analytic_code:
                                analytic_id=analytic_obj.search(cr,uid,[('name','=',analytic_code)])
                                if analytic_id:
                                    report_val['account_analytic_id'] = analytic_id[0]
                            #report with view type
                            if type=='sum':
                                report_val['type']=type
                                report_ids = acc_financial_obj.create(cr,uid,report_val,context=context)
                                
                            #report with child account analytic code
                            elif type=='account_type':
                                report_val['type']=type
                                report_ids = acc_financial_obj.create(cr,uid,report_val,context=context)
                                if account_code:
                                    for acc_type in account_code.split(','):
                                        count+=1
                                        acc_type_id=account_type_obj.search(cr,uid,[('code','=',str(acc_type))])
                                        
                                        
                                        if acc_type_id and report_ids:
                                            acc_t=account_type_obj.read(cr,uid,acc_type_id[0],{'name'})
                                            t_name=acc_t['name']
                                            cr.execute('select report_id from account_account_financial_report_type where account_type_id = %s and report_id=%s  group by report_id',(acc_type_id[0],report_ids,))
                                            exist=cr.fetchall()
                                            if len(exist)<=0:
                                                cr.execute('insert into account_account_financial_report_type(account_type_id,report_id) values(%s,%s)',(acc_type_id[0],report_ids,))
                                                #there one condition to create report with account type name and report style filter is title2
                                                if acc_type_id[0] and report_style=='title2':
                                                    type_val={'name':t_name,'sequence':count,'style_overwrite':4,'sign':1,'display_detail':'no_detail','parent_id':report_ids,'type':'account_type'}
                                                    #condition for sign
                                                    #reverse condition
                                                    if sign=='reverse':
                                                        type_val['sign']=-1
                                                    #preserve condition
                                                    elif sign=='preserve':
                                                        type_val['sign']=1
                                                    #null condition
                                                    else:
                                                        type_val['sign']=1
                                                    
                                                    report_id = acc_financial_obj.create(cr,uid,type_val,context=context)
                                                    if report_id and acc_type_id[0]:
                                                        cr.execute('select report_id from account_account_financial_report_type where account_type_id = %s and report_id=%s  group by report_id',(acc_type_id[0],report_id,))
                                                        t_exist=cr.fetchall()
                                                        if len(t_exist)<=0:
                                                            cr.execute('insert into account_account_financial_report_type(account_type_id,report_id) values(%s,%s)',(acc_type_id[0],report_id,))
                                                    
                                    
                            #report with report value
                            elif type=='account_report':
                                report_val['type']=type
                                report_ids = acc_financial_obj.create(cr,uid,report_val,context=context)
                                
                            #report with account code
                            elif type=='accounts':
                                report_val['type']=type
                                report_ids = acc_financial_obj.create(cr,uid,report_val,context=context)
                                if account_code:
                                    for acc_code in account_code.split(','):
                                        acc_count+=1
                                        account_id=account_account_obj.search(cr,uid,[('code','=',str(acc_code))])
                                        
                                        
                                        if account_id and report_ids:
                                            acc=account_account_obj.read(cr,uid,account_id[0],{'name'})
                                            acc_name=acc['name']
                                            
                                        if account_id and report_ids:
                                            cr.execute('select report_line_id from account_account_financial_report where account_id= %s and report_line_id=%s group by report_line_id',(account_id[0],report_ids,))
                                            exist=cr.fetchall()
                                            if len(exist)<=0:
                                                cr.execute('insert into account_account_financial_report(account_id,report_line_id) values(%s,%s)',(account_id[0],report_ids,)) 
                                                
                                                #there one condition to create report with account name and report style filter is title2
                                                if account_id[0] and report_style=='title2':
                                                    acc_val={'name':acc_name,'sequence':acc_count,'style_overwrite':4,'sign':1,'display_detail':'no_detail','parent_id':report_ids,'type':'accounts'}
                                                    #condition for sign
                                                    #reverse condition
                                                    if sign=='reverse':
                                                        acc_val['sign']=-1
                                                    #preserve condition
                                                    elif sign=='preserve':
                                                        acc_val['sign']=1
                                                    #null condition
                                                    else:
                                                        acc_val['sign']=1
                                                    report_id = acc_financial_obj.create(cr,uid,acc_val,context=context)
                                                    if report_id and account_id[0]:
                                                        cr.execute('select report_line_id from account_account_financial_report where account_id= %s and report_line_id=%s group by report_line_id',(account_id[0],report_id,))
                                                        t_exist=cr.fetchall()
                                                        if len(t_exist)<=0:
                                                            cr.execute('insert into account_account_financial_report(account_id,report_line_id) values(%s,%s)',(account_id[0],report_id,))
                                    
                        #parent is true and can search in financial report
                        else:
                            report_val = {'name':fr_name,'parent_id':parent_id[0],'sequence':sequence}
                            #condition for style
                            if report_style=='automatic':
                                report_val['style_overwrite']=None
                            elif report_style=='title1':
                                report_val['style_overwrite']=1
                            elif report_style=='title2':
                                report_val['style_overwrite']=2
                            elif report_style=='title3':
                                report_val['style_overwrite']=3
                            elif report_style=='normal':
                                report_val['style_overwrite']=4
                            elif report_style=='italic':
                                report_val['style_overwrite']=5
                            elif report_style=='smallest':
                                report_val['style_overwrite']=6
                            else:
                                report_val['style_overwrite']=None
                                
                            #condition for sign
                            #reverse condition
                            if sign=='reverse':
                                report_val['sign']=-1
                            #preserve condition
                            elif sign=='preserve':
                                report_val['sign']=1
                            #null condition
                            else:
                                report_val['sign']=1
                            #Report with Display Type
                            if display_type=='no detail':
                                report_val['display_detail']='no_detail'
                            elif display_type=='flat':
                                report_val['display_detail'] = 'detail_flat'
                            elif display_type=='hierarchy':
                                report_val['display_detail'] = 'detail_with_hierarchy'
                            else:
                                report_val['display_detail'] = 'no_detail'
                                
                            #analytic code
                            if analytic_code:
                                analytic_id=analytic_obj.search(cr,uid,[('name','=',analytic_code)])
                                if analytic_id:
                                    report_val['account_analytic_id'] = analytic_id[0]      
                                                                                                        
                            #report with view type
                            if type=='sum':
                                report_val['type']=type
                                report_ids = acc_financial_obj.create(cr,uid,report_val,context=context)
                                
                            #report with child account analytic code
                            elif type=='account_type':
                                report_val['type']=type
                                report_ids = acc_financial_obj.create(cr,uid,report_val,context=context)
                                if account_code:
                                    for acc_type in account_code.split(','):

                                        count+=1
                                        acc_type_id=account_type_obj.search(cr,uid,[('code','=',str(acc_type))])
                                        
                                        
                                        if acc_type_id and report_ids:
                                            acc_t=account_type_obj.read(cr,uid,acc_type_id[0],{'name'})
                                            t_name=acc_t['name']
                                        if acc_type_id and report_ids:
                                            cr.execute('select report_id from account_account_financial_report_type where account_type_id = %s and report_id=%s  group by report_id ',(acc_type_id[0],report_ids,))
                                            exist=cr.fetchall()
                                            if len(exist)<=0:
                                                cr.execute('insert into account_account_financial_report_type(account_type_id,report_id) values(%s,%s)',(acc_type_id[0],report_ids,))
                    
                                                #there one condition to create report with account type name and report style filter is title2
                                                if acc_type_id[0] and report_style=='title2':
                                                    type_val={'name':t_name,'sequence':count,'style_overwrite':4,'sign':1,'display_detail':'no_detail','parent_id':report_ids,'type':'account_type'}
                                                    #condition for sign
                                                    #reverse condition
                                                    if sign=='reverse':
                                                        type_val['sign']=-1
                                                    #preserve condition
                                                    elif sign=='preserve':
                                                        type_val['sign']=1
                                                    #null condition
                                                    else:
                                                        type_val['sign']=1
                                                    report_id = acc_financial_obj.create(cr,uid,type_val,context=context)
                                                    if report_id and acc_type_id[0]:
                                                        cr.execute('select report_id from account_account_financial_report_type where account_type_id = %s and report_id=%s  group by report_id',(acc_type_id[0],report_id,))
                                                        t_exist=cr.fetchall()
                                                        if len(t_exist)<=0:
                                                            cr.execute('insert into account_account_financial_report_type(account_type_id,report_id) values(%s,%s)',(acc_type_id[0],report_id,))
                                    
                            #report with report value
                            elif type=='account_report':
                                report_val['type']=type
                                report_ids = acc_financial_obj.create(cr,uid,report_val,context=context)
                                
                            #report with account code
                            elif type=='accounts':
                                report_val['type']=type
                                report_ids = acc_financial_obj.create(cr,uid,report_val,context=context)
                                if account_code:
                                    for acc_code in account_code.split(','):
                                        acc_count+=1
                                        account_id=account_account_obj.search(cr,uid,[('code','=',str(acc_code))])
                                        
                                        if account_id and report_ids:
                                            acc=account_account_obj.read(cr,uid,account_id[0],{'name'})
                                            acc_name=acc['name']
                                        if account_id and report_ids:
                                            cr.execute('select report_line_id from account_account_financial_report where account_id= %s and report_line_id=%s group by report_line_id',(account_id[0],report_ids,))
                                            exist=cr.fetchall()
                                            if len(exist)<=0:
                                                cr.execute('insert into account_account_financial_report(account_id,report_line_id) values(%s,%s)',(account_id[0],report_ids,)) 
                                                
                                                #there one condition to create report with account name and report style filter is title2
                                                if account_id[0] and report_style=='title2':
                                                    acc_val={'name':acc_name,'sequence':acc_count,'style_overwrite':4,'sign':1,'display_detail':'no_detail','parent_id':report_ids,'type':'accounts'}
                                                    #condition for sign
                                                    #reverse condition
                                                    if sign=='reverse':
                                                        acc_val['sign']=-1
                                                    #preserve condition
                                                    elif sign=='preserve':
                                                        acc_val['sign']=1
                                                    #null condition
                                                    else:
                                                        acc_val['sign']=1
                                                    report_id = acc_financial_obj.create(cr,uid,acc_val,context=context)
                                                    if report_id and account_id[0]:
                                                        cr.execute('select report_line_id from account_account_financial_report where account_id= %s and report_line_id=%s group by report_line_id',(account_id[0],report_id,))
                                                        t_exist=cr.fetchall()
                                                        if len(t_exist)<=0:
                                                            cr.execute('insert into account_account_financial_report(account_id,report_line_id) values(%s,%s)',(account_id[0],report_id,)) 
                                                             
                    #report with not parent    
                    else:
                        if fr_name:
                            report_id=acc_financial_obj.search(cr,uid,[('name','=',fr_name)])
                            if not report_id:
                                report_vals={'name':fr_name,'sequence':sequence}

                            #condition for style
                                if report_style=='automatic':
                                    report_vals['style_overwrite']=None
                                elif report_style=='title1':
                                    report_vals['style_overwrite']=1
                                elif report_style=='title2':
                                    report_vals['style_overwrite']=2
                                elif report_style=='title3':
                                    report_vals['style_overwrite']=3
                                elif report_style=='normal':
                                    report_vals['style_overwrite']=4
                                elif report_style=='italic':
                                    report_vals['style_overwrite']=5
                                elif report_style=='smallest':
                                    report_vals['style_overwrite']=6
                                else:
                                    report_vals['style_overwrite']=None
                                    
                                #condition for sign
                                #reverse condition
                                if sign=='reverse':
                                    report_vals['sign']=-1
                                #preserve condition
                                elif sign=='preserve':
                                    report_vals['sign']=1
                                #null condition
                                else:
                                    report_vals['sign']=1
                                #analytic code
                                if analytic_code:
                                    analytic_id=analytic_obj.search(cr,uid,[('name','=',analytic_code)])
                                    if analytic_id:
                                        report_vals['account_analytic_id'] = analytic_id[0]
                                        
                                #Report with Display Type
                                if display_type=='no detail':
                                    report_vals['display_detail']='no_detail'
                                elif display_type=='flat':
                                    report_vals['display_detail'] = 'detail_flat'
                                elif display_type=='hierarchy':
                                    report_vals['display_detail'] = 'detail_with_hierarchy'
                                else:
                                    report_vals['display_detail'] = 'no_detail'
                                                                                                              
                                #report with view type
                                if type=='sum':
                                    report_vals['type']=type
                                    report_ids = acc_financial_obj.create(cr,uid,report_vals,context=context)
                                    
                                #report with child account analytic code
                                elif type=='account_type':
                                    report_vals['type']=type
                                    report_ids = acc_financial_obj.create(cr,uid,report_vals,context=context)
                                    if account_code:
                                        for acc_type in account_code.split(','):

                                            count+=1
                                            acc_type_id=account_type_obj.search(cr,uid,[('code','=',str(acc_type))])
                                            
                                            
                                            if acc_type_id and report_ids:
                                                acc_t = account_type_obj.read(cr,uid,acc_type_id[0],{'name'})
                                                t_name = acc_t['name']
                                                
                                            if acc_type_id and report_ids:
                                                cr.execute('select report_id from account_account_financial_report_type where account_type_id = %s and report_id=%s  group by report_id',(acc_type_id[0],report_ids,))
                                                exist=cr.fetchall()
                                                
                                                if len(exist)<=0:
                                                    cr.execute('insert into account_account_financial_report_type(account_type_id,report_id) values(%s,%s)',(acc_type_id[0],report_ids,))
                                        
                                                    #there one condition to create report with account type name and report style filter is title2
                                                    if acc_type_id[0] and report_style=='title2':
                                                        type_val={'name':t_name,'sequence':count,'style_overwrite':4,'sign':1,'display_detail':'no_detail','parent_id':report_ids,'type':'account_type'}
                                                        #condition for sign
                                                        #reverse condition
                                                        if sign=='reverse':
                                                            type_val['sign']=-1
                                                        #preserve condition
                                                        elif sign=='preserve':
                                                            type_val['sign']=1
                                                        #null condition
                                                        else:
                                                            type_val['sign']=1
                                                        report_id = acc_financial_obj.create(cr,uid,type_val,context=context)
                                                        if report_id and acc_type_id[0]:
                                                            cr.execute('select report_id from account_account_financial_report_type where account_type_id = %s and report_id=%s  group by report_id',(acc_type_id[0],report_id,))
                                                            t_exist=cr.fetchall()
                                                            if len(t_exist)<=0:
                                                                cr.execute('insert into account_account_financial_report_type(account_type_id,report_id) values(%s,%s)',(acc_type_id[0],report_id,))
                                #report with report value
                                elif type=='account_report':
                                    report_vals['type']=type
                                    report_ids = acc_financial_obj.create(cr,uid,report_vals,context=context)
                                    
                                #report with account code
                                elif type=='accounts':
                                    report_vals['type']=type
                                    report_ids = acc_financial_obj.create(cr,uid,report_vals,context=context)
                                    if account_code:
                                        for acc_code in account_code.split(','):
                                            acc_count+=1
                                            account_id=account_account_obj.search(cr,uid,[('code','=',str(acc_code))])
                                            
                                            
                                            if account_id and report_ids:
                                                acc=account_account_obj.read(cr,uid,account_id[0],{'name'})
                                                acc_name=acc['name']
                                                
                                            if account_id and report_ids:
                                                cr.execute('select report_line_id from account_account_financial_report where account_id= %s and report_line_id=%s group by report_line_id',(account_id[0],report_ids,))
                                                exist=cr.fetchall()
                                                
                                                if len(exist)<=0:
                                                    cr.execute('insert into account_account_financial_report(account_id,report_line_id) values(%s,%s)',(account_id[0],report_ids,)) 
                                                    
                                                    #there one condition to create report with account name and report style filter is title2
                                                    if account_id[0] and report_style=='title2':
                                                        acc_val={'name':acc_name,'sequence':acc_count,'style_overwrite':4,'sign':1,'display_detail':'no_detail','parent_id':report_ids,'type':'accounts'}
                                                        #condition for sign
                                                        #reverse condition
                                                        if sign=='reverse':
                                                            acc_val['sign']=-1
                                                        #preserve condition
                                                        elif sign=='preserve':
                                                            acc_val['sign']=1
                                                        #null condition
                                                        else:
                                                            acc_val['sign']=1
                                                        report_id = acc_financial_obj.create(cr,uid,acc_val,context=context)
                                                        if report_id and account_id[0]:
                                                            cr.execute('select report_line_id from account_account_financial_report where account_id= %s and report_line_id=%s group by report_line_id',(account_id[0],report_id,))
                                                            t_exist=cr.fetchall()
                                                            if len(t_exist)<=0:
                                                                cr.execute('insert into account_account_financial_report(account_id,report_line_id) values(%s,%s)',(account_id[0],report_id,)) 

                except Exception, e:
                    raise    
                self.write(cr, uid, ids[0], {'state': 'completed'})              


        
