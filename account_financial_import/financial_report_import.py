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
header_fields = ['company', 'fr name', 'sequence', 'type', 'parent a/c', 'sign', 'financial report style', 'coa name', 'account code', 'display type', 'analytic code']

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
    
    _constraints = [(_check_file_ext, "Please import Excel file!", ['import_fname'])]
    
    def import_data(self, cr, uid, ids, context=None):
        acc_financial_obj = self.pool.get('account.financial.report')
        account_account_obj = self.pool.get('account.account')
        account_type_obj = self.pool.get('account.account.type')
        # for analytic account code
        analytic_obj = self.pool.get('account.analytic.account')
        # for analytic id checking
        cr.execute('select id ,name from account_analytic_account')
        analytic_value = cr.fetchall()
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
                    company_i = fr_name_i = sequence_i = type_i = parent_ac_i = display_type_i = sign_i = report_style_i = coa_name_i = account_code_i = display_code_i = analytic_code_i = None
                    column_cnt = 0
                    i = 0
                    for cnt in range(len(ln)):
                        if ln[cnt] == '':
                            column_cnt = cnt
                            break
                        elif cnt == len(ln) - 1:
                            column_cnt = cnt + 1
                            break
                    for i in range(column_cnt):
                        # header fields
                        header_field = ln[i].strip().lower()
                        if header_field not in header_fields:
                            err_log += '\n' + _("Invalid Excel File, Header Field '%s' is not supported !") % ln[i]
                        # required header fields : account, debit, credit
                        
                        elif header_field == 'fr name':
                            fr_name_i = i
                        elif header_field == 'sequence':
                            sequence_i = i
                        elif header_field == 'type':
                            type_i = i
                        elif header_field == 'parent a/c':
                            parent_ac_i = i
                        elif header_field == 'sign':
                            sign_i = i
                        elif header_field == 'financial report style':
                            report_style_i = i            
                        elif header_field == 'coa name':
                            coa_name_i = i
                        elif header_field == 'account code':
                            account_code_i = i
                        elif header_field == 'display type':
                            display_type_i = i
                        elif header_field == 'analytic code':
                            analytic_code_i = i
                        elif header_field == 'company':
                            company_i = i
                                      
                    for f in [(company_i, 'company'), (analytic_code_i, 'analytic code'), (display_type_i, 'display type'), (fr_name_i, 'fr name'), (sequence_i, 'sequence'), (type_i, 'type'), (sign_i, 'sign'), (parent_ac_i, 'parent a/c'), (report_style_i , 'financial report style'), (coa_name_i, 'coa name'), (account_code_i, 'account code')]:
                        if not isinstance(f[0], int):
                            err_log += '\n' + _("Invalid Excel file, Header '%s' is missing !") % f[1]
                        
                # process data lines   
            else:
                # add the without value for without header fields columns
                for i in range(0, val):
                    ln.append('')
                if ln and ln[0] and ln[0][0] not in ['#', '']:
                    try:
                        import_vals = {}
                        import_vals['fr name'] = ln[fr_name_i]
                        import_vals['sequence'] = ln[sequence_i] 
                        import_vals['type'] = ln[type_i]
                        import_vals['parent a/c'] = ln[parent_ac_i]
                        import_vals['sign'] = ln[sign_i]
                        import_vals['financial report style'] = ln[report_style_i]   
                        import_vals['coa name'] = ln[coa_name_i]     
                        import_vals['account code'] = ln[account_code_i]  
                        import_vals['display type'] = ln[display_type_i]           
                        import_vals['analytic code'] = ln[analytic_code_i]      
                        import_vals['company'] = ln[company_i]                
                        amls.append(import_vals)
                    except Exception , e:
                        print e
                  
        if err_log:
            self.write(cr, uid, ids[0], {'note': err_log})
            self.write(cr, uid, ids[0], {'state': 'error'})
        else:
            for aml in amls:
                try:
                    company = fr_name = sequence = type = coa_name = parent = sign = report_style = account_code = display_type = analytic_code = parent_id = None
                    count = acc_count = 0
                    parent_report_val = report_val = {}
                    company_id = analytic_id = None
                    # some font type is Unicode so I use UTF-8 encoding
                    
                    try:
                        if aml['company']:
                            company = str(aml['company']).strip()
                            cr.execute(""" select id from res_company where lower(name) = %s """, (company.lower(),))
                            data = cr.fetchall()
                            if data:
                                try:
                                    company_id = data[0][0]
                                except:
                                    company_id = data[0]
                    except:
                        company_id = None
                        
                    try:
                        if aml['fr name']:
                            fr_name = str(aml['fr name'].encode('utf-8'))
                            fr_name = fr_name.strip()
                        else:
                            fr_name = None
                            
                        if aml['account code']:
                            account_code = str(aml['account code'])
                            account_code = account_code.strip()
                        else:
                            account_code = None
                            
                        # I wish to change parent code to .title() but there some report names are same but all cap letter and also small letter. 
                        if aml['parent a/c']:
                            parent = str(aml['parent a/c'].encode('utf-8'))
                            parent = parent.strip()
                        else:
                            parent = None
                            
                        if aml['type']:
                            type = str(aml['type'].encode('utf-8'))
                            type = type.strip()
                            if type == 'View':
                                type = 'sum'
                            elif type == 'Accounts':
                                type = 'accounts'
                            elif type == 'Report Value':
                                type = 'account_report'
                            elif type == 'Account type':
                                type = 'account_type'
                        else:
                            type = None
                               
                        if aml['sequence']:
                            try:
                                sequence = int(aml['sequence'])
                            except Exception, e:  
                                sequence = aml['sequence']
                        else:
                            sequence = None
                            
                        if aml['financial report style']:
                            report_style = str(aml['financial report style'])
                            report_style = report_style.strip()
                        else:
                            report_style = None
                        # no used coa name in program    
                        if aml['coa name']:
                            coa_name = str(aml['coa name'].encode('utf-8'))
                            coa_name = coa_name.strip()
                        else:
                            coa_name = None
                        
                        if aml['sign']:
                            sign = str(aml['sign']).lower()
                            sign = sign.strip()
                        else:
                            sign = None
                       
                        # No Detail , Display with flat , Display with hierarchy
                        if aml['display type'] :
                            try:
                                display_type = int(aml['display type'])
                            except Exception, e:    
                                dispaly_type = aml['display type']
                        else:
                            dispaly_type = None     
                            
                        # analytic code
                        if aml['analytic code']:
                            try:
                                analytic_code = str(aml['analytic code']).strip() 
                                analytic_code = analytic_code.lower()   
                            except Exception , e:
                                raise e
                        else:
                            analytic_code = None
                    except Exception, e:    
                        raise e
                        
                        
                    # FIRST   
                    # REPORT with parent
                    
                    if fr_name:
                        #report_id = acc_financial_obj.search(cr, uid, [('name', '=', fr_name), ('company_id', '=', company_id)])
                        report_id = acc_financial_obj.search(cr, uid, [('name', '=', fr_name)])
                        # #condition for parent report
                        if parent:
                            #parent_ids = acc_financial_obj.search(cr, uid, [('name', '=', parent), ('company_id', '=', company_id)])
                            parent_ids = acc_financial_obj.search(cr, uid, [('name', '=', parent)])
                            if not parent_ids:
                                parent_report_val = {
                                            'name':parent,
                                            'sequence':0 ,
                                            'parent_id':None,
                                            'style_overwrite':1,
                                            'sign':1,
                                            'display_detail':'no_detail',
                                            'company_id':company_id
                                }
                                parent_id = acc_financial_obj.create(cr, uid, parent_report_val, context=context)
                            else:
                                parent_id = parent_ids[0]
                                
                        # if already exist update
                        if report_id:
                            report_id = report_id[0]
                            #report_val = {'name':fr_name, 'sequence':sequence , 'parent_id':parent_id, 'company_id':company_id}
                            report_val = {'name':fr_name, 'sequence':sequence , 'parent_id':parent_id}
                            if report_style == 'automatic':
                                report_val['style_overwrite'] = None
                            elif report_style == 'title1':
                                report_val['style_overwrite'] = 1
                            elif report_style == 'title2':
                                report_val['style_overwrite'] = 2
                            elif report_style == 'title3':
                                report_val['style_overwrite'] = 3
                            elif report_style == 'normal':
                                report_val['style_overwrite'] = 4
                            elif report_style == 'italic':
                                report_val['style_overwrite'] = 5
                            elif report_style == 'smallest':
                                report_val['style_overwrite'] = 6
                            else:
                                report_val['style_overwrite'] = None
                                 
                            # condition for sign
                            # reverse condition
                            if sign == 'reverse':
                                report_val['sign'] = -1
                            # preserve condition
                            elif sign == 'preserve':
                                report_val['sign'] = 1
                            # null condition
                            else:
                                report_val['sign'] = 1
                                
                            # Report with display type
                            if display_type == 1:
                                report_val['display_detail'] = 'no_detail'
                            elif display_type == 2:
                                report_val['display_detail'] = 'detail_flat'
                            elif display_type == 3:
                                report_val['display_detail'] = 'detail_with_hierarchy'
                            else:
                                report_val['display_detail'] = 'no_detail'
                             
                            # analytic code
                            if analytic_code and analytic_value:
                                # analytic_id=analytic_obj.search(cr,uid,[('name','=',analytic_code)])
                                for aa_code in analytic_value:
                                    if analytic_code == aa_code[1].lower():
                                        analytic_id = aa_code[0]
                                if analytic_id:
                                    
                                    report_val['account_analytic_id'] = analytic_id
                            # report with view type
                            if type == 'sum':
                                report_val['type'] = type
                                acc_financial_obj.write(cr, uid, report_id, report_val, context=context)
                                 
                            # report with child account analytic code
                            elif type == 'account_type':
                                report_val['type'] = type
                                acc_financial_obj.write(cr, uid, report_id, report_val, context=context)
                                report_ids = report_id
                                if account_code:
                                    for acc_type in account_code.split(','):
                                        count += 1
                                        if acc_type.find('.') != -1:
                                            acc_type = acc_type.split('.')[0]
                                        else:
                                            acc_type = int(acc_type)
                                        #acc_type_id = account_type_obj.search(cr, uid, [('code', '=', str(acc_type)), ('compay_id', '=', company_id)])
                                        acc_type_id = account_type_obj.search(cr, uid, [('code', '=', str(acc_type))])
                                         
                                         
                                        if acc_type_id and report_ids:
                                            cr.execute('select report_id from account_account_financial_report_type where account_type_id = %s and report_id=%s  group by report_id', (acc_type_id[0], report_ids,))
                                            exist = cr.fetchall()
                                            if len(exist) <= 0:
                                                cr.execute('insert into account_account_financial_report_type(account_type_id,report_id) values(%s,%s)', (acc_type_id[0], report_ids,))                                       
                                     
                            # report with report value
                            elif type == 'account_report':
                                report_val['type'] = type
                                acc_financial_obj.write(cr, uid, report_id, report_val, context=context)
                                 
                            # report with account code
                            elif type == 'accounts':
                                report_val['type'] = type
                                acc_financial_obj.write(cr, uid, report_id, report_val, context=context)
                                report_ids = report_id
                                if account_code:
                                    for acc_code in account_code.split(','):
                                        acc_count += 1
                                        # dot par lar yin
                                        if acc_code.find('.') != -1:
                                            acc_code = acc_code.split('.')[0]
                                        else:
                                            acc_code = int(acc_code)
                                        account_id = account_account_obj.search(cr, uid, [('code', '=', str(acc_code)), ('company_id', '=', company_id)])

                                        if account_id and report_ids:
                                            cr.execute('select report_line_id from account_account_financial_report where account_id= %s and report_line_id=%s group by report_line_id', (account_id[0], report_ids,))
                                            exist = cr.fetchall()
                                            if len(exist) <= 0:
                                                cr.execute('insert into account_account_financial_report(account_id,report_line_id) values(%s,%s)', (account_id[0], report_ids,))                
                        # There no report id in account_financial_report                                
                        elif not report_id:
                            # condition for style
                            #report_val = {'name':fr_name, 'sequence':sequence , 'parent_id':parent_id, 'company_id':company_id}
                            report_val = {'name':fr_name, 'sequence':sequence , 'parent_id':parent_id}
                            if report_style == 'automatic':
                                report_val['style_overwrite'] = None
                            elif report_style == 'title1':
                                report_val['style_overwrite'] = 1
                            elif report_style == 'title2':
                                report_val['style_overwrite'] = 2
                            elif report_style == 'title3':
                                report_val['style_overwrite'] = 3
                            elif report_style == 'normal':
                                report_val['style_overwrite'] = 4
                            elif report_style == 'italic':
                                report_val['style_overwrite'] = 5
                            elif report_style == 'smallest':
                                report_val['style_overwrite'] = 6
                            else:
                                report_val['style_overwrite'] = None
                                 
                            # condition for sign
                            # reverse condition
                            if sign == 'reverse':
                                report_val['sign'] = -1
                            # preserve condition
                            elif sign == 'preserve':
                                report_val['sign'] = 1
                            # null condition
                            else:
                                report_val['sign'] = 1
                                
                            # Report with display type
                            if display_type == 1:
                                report_val['display_detail'] = 'no_detail'
                            elif display_type == 2:
                                report_val['display_detail'] = 'detail_flat'
                            elif display_type == 3:
                                report_val['display_detail'] = 'detail_with_hierarchy'
                            else:
                                report_val['display_detail'] = 'no_detail'
                             
                            # analytic code
                            if analytic_code and analytic_value:
                                for aa_code in analytic_value:
                                    if analytic_code == aa_code[1].lower():
                                        analytic_id = aa_code[0]
                                if analytic_id:
                                    report_val['account_analytic_id'] = analytic_id
                            # report with view type
                            if type == 'sum':
                                report_val['type'] = type
                                report_ids = acc_financial_obj.create(cr, uid, report_val, context=context)
                                 
                            # report with child account analytic code
                            elif type == 'account_type':
                                report_val['type'] = type
                                report_ids = acc_financial_obj.create(cr, uid, report_val, context=context)
                                if account_code:
                                    for acc_type in account_code.split(','):
                                        count += 1
                                        if acc_type.find('.') != -1:
                                            acc_type = acc_type.split('.')[0]
                                        else:
                                            acc_type = int(acc_type)
                                        acc_type_id = account_type_obj.search(cr, uid, [('code', '=', str(acc_type))])
                                         
                                         
                                        if acc_type_id and report_ids:
                                            cr.execute('select report_id from account_account_financial_report_type where account_type_id = %s and report_id=%s  group by report_id', (acc_type_id[0], report_ids,))
                                            exist = cr.fetchall()
                                            if len(exist) <= 0:
                                                cr.execute('insert into account_account_financial_report_type(account_type_id,report_id) values(%s,%s)', (acc_type_id[0], report_ids,))                                            
                                     
                            # report with report value
                            elif type == 'account_report':
                                report_val['type'] = type
                                report_ids = acc_financial_obj.create(cr, uid, report_val, context=context)
                                 
                            # report with account code
                            elif type == 'accounts':
                                report_val['type'] = type
                                report_ids = acc_financial_obj.create(cr, uid, report_val, context=context)
                                if account_code:
                                    for acc_code in account_code.split(','):
                                        acc_count += 1
                                        # some account code contain dot operator and I can't search it,so I split it.
                                        if acc_code.find('.') != -1:
                                            acc_code = acc_code.split('.')[0]
                                        else:
                                            acc_code = int(acc_code)
                                        account_id = account_account_obj.search(cr, uid, [('code', '=', str(acc_code)), ('company_id', '=', company_id)])
                                        
                                        if account_id and report_ids:
                                            cr.execute('select report_line_id from account_account_financial_report where account_id= %s and report_line_id=%s group by report_line_id', (account_id[0], report_ids,))
                                            exist = cr.fetchall()
                                            if len(exist) <= 0:
                                                cr.execute('insert into account_account_financial_report(account_id,report_line_id) values(%s,%s)', (account_id[0], report_ids,)) 
                                                 
                except Exception, e:
                    raise  e
                self.write(cr, uid, ids[0], {'state': 'completed'})              