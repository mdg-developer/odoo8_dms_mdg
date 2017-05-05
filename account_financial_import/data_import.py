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
header_fields = ['name','code','parent','type','detail','level']

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
        account_report_line_obj=self.pool.get('account.account.financial.report')
        account_type_obj=self.pool.get('account.account.type')
        profit_and_loss_id=acc_financial_obj.search(cr,uid,['&',('name','=','损益(Profit and Loss)'),('level','=',0)])
        balance_sheet_id=acc_financial_obj.search(cr,uid,['&',('name','=','资产负债表(Balance Sheet)'),('level','=',0)])
        if profit_and_loss_id:
            p_id=int(profit_and_loss_id[0])
        else:
            val={'name':'损益(Profit and Loss)','type':'sum','display_detail':'detail_flat','level':0,'sequence':0}
            profit_and_loss_id=acc_financial_obj.create(cr,uid,val,context=context)
            p_id=int(profit_and_loss_id)
        if balance_sheet_id:
            print 'this is balance sheet id',balance_sheet_id
            b_id=int(balance_sheet_id[0])
        else:
            val={'name':'资产负债表(Balance Sheet)','type':'sum','display_detail':'detail_flat','level':0,'sequence':0}
            balance_sheet_id=acc_financial_obj.create(cr,uid,val,context=context)
            b_id=int(balance_sheet_id)
        cr.execute('delete from account_account_financial_report')
        cr.execute('delete from account_account_financial_report_type')
        ir_model_fields_obj=self.pool.get('ir.model.fields')
        ir_property_obj = self.pool.get('ir.property')
        data = self.browse(cr,uid,ids)[0]
        file_name=data['import_fname']
        company_id = data.company_id.id
        import_file = data.import_file
        import_filename = data.name
        print 'import_file',import_file
        print 'import_filename',import_filename
        err_log = ''
        header_line = False
        if file_name.find('.csv')!=-1:
            err_log = ''
            header_line = False 
            csv_file_import = True
            csv_data = base64.decodestring(import_file)
            r = csv.reader(StringIO.StringIO(csv_data), delimiter=",")
            print 'r', r
            amls=[]
            for ln in r:
                if not ln or ln and ln[0] and ln[0][0] in ['', '#']:
                    continue
                
                # process header line
                if not header_line:
                    if ln[0].strip() not in header_fields:
                        raise orm.except_orm(_('Error :'), _("Error while processing the header line %s. \n\nPlease check your CSV separator as well as the column header fields") % ln)
                    else:
                        header_line = True
                        name_i = code_i = parent_i = type_i = detail_i = level_i = None
                        column_cnt = 0
                        for cnt in range(len(ln)):
                            if ln[cnt] == '':
                                column_cnt = cnt
                                break
                            elif cnt == len(ln) - 1:
                                column_cnt = cnt + 1
                                break
                        for i in range(column_cnt):
                            # header fields
                            header_field = ln[i].strip()
                            if header_field not in header_fields:
                                err_log += '\n' + _("Invalid CSV File, Header Field '%s' is not supported !") % ln[i]
                            # required header fields : account, debit, credit
                            elif header_field == 'name':
                                name_i = i
                            elif header_field == 'code':
                                code_i = i
                            elif header_field == 'parent':
                                parent_i = i
                            elif header_field == 'detail':
                                detail_i = i
                            elif header_field == 'level':
                                level_i = i
                            elif header_field == 'type':
                                type_i = i
                        for f in [(name_i, 'name'), (code_i, 'code'), (parent_i, 'parent'), (detail_i, 'detail'), (type_i, 'type'),(level_i ,'level')]:
                            if not isinstance(f[0], int):
                                err_log += '\n' + _("Invalid CSV file, Header '%s' is missing !") % f[1]
                            
                    # process data lines   
                else:
                    if ln and ln[0] and ln[0][0] not in ['#', '']:
                        
                        import_vals = {}
                        import_vals['name'] = ln[name_i]
                        import_vals['code'] = ln[code_i]
                        import_vals['parent'] = ln[parent_i]
                        import_vals['detail'] = ln[detail_i]
                        import_vals['type'] = ln[type_i]
                        import_vals['level'] = ln[level_i]
                        amls.append(import_vals)
                        
            if err_log:
                self.write(cr, uid, ids[0], {'note': err_log})
                self.write(cr, uid, ids[0], {'state': 'failed'})
            else:
                for aml in amls:
                    try:
                        level= code = name = parent = view_type = detail= acc_id =acc_type_id = name_id=None
                        acc_val=acc_val1 = None
                        val={}
                        name=aml['name']
                        code=aml['code']
                        if code=='':
                            code=0
                        parent_code=str(aml['parent'])
                        print 'parent id',parent_code
                        type=str(aml['type'])
                        detail=aml['detail']
                        sequence=int(aml['level'])
                        print 'level ',aml['level']
        #---------------------------Profit And Loss---------------------------
                        ##Check the Report type is Profit And Loss or not
                        if parent_code.title()=='Profitandloss':
                            val_p_and_l={'name':name,'sequence':sequence,'type':'sum','display_detail':'detail_flat','sign':1,'parent_id':p_id}
                            p_and_l_id=acc_financial_obj.search(cr,uid,[('name','=',name)])
                            if not p_and_l_id:
                                acc_financial_obj.create(cr,uid,val_p_and_l,context=context)
                                print 'create Profit and Loss'
                            else:
                                acc_financial_obj.write(cr,uid,p_and_l_id[0],val_p_and_l)
                        elif parent_code.title()=='Balancesheet':
                            val_b_s={'name':name,'sequence':sequence,'type':'sum','display_detail':'detail_flat','sign':1,'parent_id':b_id}
                            p_and_l_id=acc_financial_obj.search(cr,uid,[('name','=',name)])
                            if not p_and_l_id:
                                print 'value',val_b_s
                                acc_financial_obj.create(cr,uid,val_b_s,context=context)
                                print 'create Balance Sheet'
                            else:
                                acc_financial_obj.write(cr,uid,p_and_l_id[0],val_b_s)
                        ###If 
                        else:
                            if parent_code:
                                print 'create'
                                parent_id=acc_financial_obj.search(cr,uid,[('name','=',parent_code)])
                                print 'parent_id',parent_id
                                if parent_id:
                                    view_type=acc_financial_obj.read(cr,uid,parent_id[0],['type'])
                                    print 'view',view_type['type']
                                    if view_type['type']=='accounts':
                                        print 'this is account code',code
                                        acc_id=account_account_obj.search(cr,uid,[('code','=',int(code))])
                                        if not acc_id:
                                            print 'there have no account code in account table.'
                                        else:
                                            cr.execute('insert into account_account_financial_report(account_id,report_line_id) values(%s,%s)',(acc_id[0],parent_id[0],))
                                            print 'need to take account code from account account table.'
                                        
                                    elif view_type['type']=='account_type':
                                        acc_type_id=account_type_obj.search(cr,uid,[('code','=',str(code))])
                                        if not acc_type_id:
                                            print 'there have no account code in account table.'
                                        else:
                                            cr.execute('insert into account_account_financial_report_type(account_type_id,report_id) values(%s,%s)',(acc_type_id[0],parent_id[0],))
                                            print 'need to take account code from account account table.'
                                    else:
                                        acc_val={'name':name,'sequence':sequence,'type':type,'display_detail':detail,'sign':1,'parent_id':parent_id[0]}
                                        print 'Only create the report value and done.If view type is normal type create normal report.'
                                        name_id=acc_financial_obj.search(cr,uid,[('name','=',name)])
                                        if not name_id:
                                            acc_financial_obj.create(cr,uid,acc_val,context=context)
                                        else:
                                            acc_financial_obj.write(cr,uid,name_id[0],acc_val)
                                else:
                                    
                                    print 'view not like',view_type
                            else:
                                print 'not create'
                    except Exception, e:
                        raise    
                self.write(cr, uid, ids[0], {'state': 'completed'})
            print amls
        else:
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
                        level_i = code_i = name_i = parent_i = type_i = detail_i = None
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
                            elif header_field == 'level':
                                level_i = i
                            elif header_field == 'code':
                                code_i = i
                            elif header_field == 'name':
                                name_i = i
                            elif header_field == 'parent':
                                parent_i = i
                            elif header_field == 'type':
                                type_i = i 
                            elif header_field == 'detail':
                                detail_i = i                           
                        for f in [(level_i,'id'),(code_i,'code'),(name_i,'name'),(parent_i,'parent'),(type_i,'type'),(detail_i ,'detail')]:
                            if not isinstance(f[0],int):
                                err_log += '\n'+ _("Invalid CSV file, Header '%s' is missing !") % f[1]
                            
                    #process data lines   
                else:
                    if ln and ln[0] and ln[0][0] not in ['#','']:
                        
                        import_vals = {}
                        import_vals['level'] =  ln[level_i]
                        import_vals['code'] =  ln[code_i] 
                        import_vals['name'] =  ln[name_i]
                        import_vals['parent'] =  ln[parent_i]
                        import_vals['type'] =  ln[type_i]
                        import_vals['detail'] =  ln[detail_i]                                   
                        amls.append(import_vals)
                      
            if err_log:
                self.write(cr, uid, ids[0], {'note': err_log})
                self.write(cr, uid, ids[0], {'state': 'failed'})
            else:
                for aml in amls:
                    try:
                        level= code = name = parent = view_type = detail= acc_id =acc_type_id = name_id=None
                        acc_val=acc_val1 = None
                        val={}
                        name=aml['name'].encode('utf-8')
                        print 'name',name.title()
                        code=aml['code']
                        if code=='':
                            code=0
                        parent_code=str(aml['parent'].encode('utf-8'))
                        print 'parent id',parent_code
                        type=str(aml['type'].encode('utf-8'))
                        detail=aml['detail'].encode('utf-8')
                        sequence=int(aml['level'])
                        print 'level ',aml['level']
        #---------------------------Profit And Loss---------------------------
                        ##Check the Report type is Profit And Loss or not
                        if parent_code.title()=='Profitandloss':
                            val_p_and_l={'name':name,'sequence':sequence,'type':'sum','display_detail':'detail_flat','sign':1,'parent_id':p_id}
                            p_and_l_id=acc_financial_obj.search(cr,uid,[('name','=',name)])
                            if not p_and_l_id:
                                acc_financial_obj.create(cr,uid,val_p_and_l,context=context)
                                print 'create Profit and Loss'
                            else:
                                acc_financial_obj.write(cr,uid,p_and_l_id[0],val_p_and_l)
                        elif parent_code.title()=='Balancesheet':
                            val_b_s={'name':name,'sequence':sequence,'type':'sum','display_detail':'detail_flat','sign':1,'parent_id':b_id}
                            p_and_l_id=acc_financial_obj.search(cr,uid,[('name','=',name)])
                            if not p_and_l_id:
                                print 'value',val_b_s
                                acc_financial_obj.create(cr,uid,val_b_s,context=context)
                                print 'create Balance Sheet'
                            else:
                                acc_financial_obj.write(cr,uid,p_and_l_id[0],val_b_s)
                        ###If 
                        else:
                            if parent_code:
                                print 'create'
                                parent_id=acc_financial_obj.search(cr,uid,[('name','=',parent_code)])
                                print 'parent_id',parent_id
                                if parent_id:
                                    view_type=acc_financial_obj.read(cr,uid,parent_id[0],['type'])
                                    print 'view',view_type['type']
                                    if view_type['type']=='accounts':
                                        print 'this is account code',code
                                        acc_id=account_account_obj.search(cr,uid,[('code','=',int(code))])
                                        if not acc_id:
                                            print 'there have no account code in account table.'
                                        else:
                                            cr.execute('insert into account_account_financial_report(account_id,report_line_id) values(%s,%s)',(acc_id[0],parent_id[0],))
                                            print 'need to take account code from account account table.'
                                        
                                    elif view_type['type']=='account_type':
                                        acc_type_id=account_type_obj.search(cr,uid,[('code','=',str(code))])
                                        if not acc_type_id:
                                            print 'there have no account code in account table.'
                                        else:
                                            cr.execute('insert into account_account_financial_report_type(account_type_id,report_id) values(%s,%s)',(acc_type_id[0],parent_id[0],))
                                            print 'need to take account code from account account table.'
                                    else:
                                        acc_val={'name':name,'sequence':sequence,'type':type,'display_detail':detail,'sign':1,'parent_id':parent_id[0]}
                                        print 'Only create the report value and done.If view type is normal type create normal report.'
                                        name_id=acc_financial_obj.search(cr,uid,[('name','=',name)])
                                        if not name_id:
                                            acc_financial_obj.create(cr,uid,acc_val,context=context)
                                        else:
                                            acc_financial_obj.write(cr,uid,name_id[0],acc_val)
                                else:
                                    
                                    print 'view not like',view_type
                            else:
                                print 'not create'
                    except Exception, e:
                        raise    
                self.write(cr, uid, ids[0], {'state': 'completed'})
            print amls
                    
                        
                            


        
