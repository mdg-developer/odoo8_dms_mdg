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
import xlrd
from xlrd import open_workbook
from openerp.tools.translate import _
from datetime import datetime
import base64
import logging
from __builtin__ import True
_logger = logging.getLogger(__name__)
header_fields = ['day', 'sale_team', 'customer_code', 'main_group', 'date', 'branch', 'principal']

class sale_plans_import(osv.osv):
    _name = 'sale.plans.import'
    _columns = {
              'name':fields.char('Description'),
              'import_date':fields.date('Import Date', readonly=True),
              'import_fname': fields.char('Filename', size=128),
              'import_file':fields.binary('File', required=True),
              'note':fields.text('Log'),
              'company_id': fields.many2one('res.company', 'Company', required=False),
              'action':fields.selection([('sale_plan_day', 'Sale Plan Day'), ('sale_plan_trip', 'Sale Plan Trip')], 'Import Table', required=True),
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
    
    _constraints = [(_check_file_ext, "Please import Excel file!", ['import_fname'])]
    
    def button_click(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids)[0]
        action = data.action
        if action == 'sale_plan_day':
            print 'sale_plan_day sale_plan_day'
            self.import_sale_plan_day(cr, uid, ids, context=context)
        elif action == 'sale_plan_trip':
            self.import_sale_plan_trip(cr, uid, ids, context=context)
        return True
    def import_sale_plan_day(self, cr, uid, ids, context=None):

        sale_plan_day_obj = self.pool.get('sale.plan.day')
        maingroup_obj = self.pool.get('product.maingroup')
        principal_obj = self.pool.get('product.principal')
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
                if head_count < 3:
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
                    day_plan_i = sale_team_i = customer_code_i = main_group_i = date_i = branch_i = principal_i = None
                    column_cnt = len(ln)
                    for i in range(column_cnt):
                        # header fields
                        header_field = ln[i].strip().lower()
                        if header_field not in header_fields:
                            err_log += '\n' + _("Invalid Excel File, Header Field '%s' is not supported !") % ln[i]
                        # required header fields : account, debit, credit
                        elif header_field == 'day':
                            day_plan_i = i
                        elif header_field == 'sale_team':
                            sale_team_i = i
                        elif header_field == 'customer_code':
                            customer_code_i = i
                        elif header_field == 'main_group':
                            main_group_i = i
                        elif header_field == 'date':
                            date_i = i
                        elif header_field == 'branch':
                            branch_i = i
                        elif header_field == 'principal':
                            principal_i = i
                    for f in [(principal_i, 'principal'), (day_plan_i, 'day'), (sale_team_i, 'sale_team'), (customer_code_i, 'customer_code'), (main_group_i, 'main_group'), (date_i, 'date'), (branch_i, 'branch')]:
                        if not isinstance(f[0], int):
                            err_log += '\n' + _("Invalid Excel file, Header '%s' is missing !") % f[1]
                        
                # process data lines   
            else:
                # add the without value for without header fields columns
                for i in range(0, val):
                    ln.append('')
                if ln and ln[0] and ln[0][0] not in ['#', '']:
                    import_vals = {}
                    import_vals['day'] = ln[day_plan_i]
                    import_vals['sale_team'] = ln[sale_team_i]
                    import_vals['customer_code'] = ln[customer_code_i]
                    import_vals['main_group'] = ln[main_group_i]
                    import_vals['date'] = ln[date_i]
                    import_vals['branch'] = ln[branch_i]
                    import_vals['principal'] = ln[principal_i]
                    amls.append(import_vals)
       
        if err_log:
            self.write(cr, uid, ids[0], {'note': err_log})
            self.write(cr, uid, ids[0], {'state': 'error'})
        if amls or err_log:
            try:
                for aml in amls:
                        print 'aml', aml
                        day_plan = sale_team = sale_team_id = customer_code = main_group = main_group_id = principal_id = date = branch = branch_id = plan_id = customer_id = customer_code = None
                        data = None
                        
                        if aml['principal']:
                            principal = str(aml['principal']).strip()
                            principal = principal.replace(".0", "")
                            cr.execute("""select id from product_principal where lower(name) like %s """, (principal.lower(),))
                            data = cr.fetchall()
                            if data:
                                principal_id = data[0][0]
                            else:
                                principal_id = principal_obj.create(cr, uid, {'name':principal}, context=context)
                        if aml['day']:
                            day_plan = str(aml['day']).strip()
                        else:
                            day_plan = None
                            
                        if aml['sale_team']:
                            sale_team = str(aml['sale_team']).strip()
                            cr.execute('select id from crm_case_section where lower(complete_name) like %s', (sale_team.lower(),))
                            sale_team_ids = cr.fetchall()
                            if sale_team_ids:
                                sale_team_id = sale_team_ids[0]
                            else:
                                sale_team_id = None
                        else:
                            sale_team = ''
                            sale_team_id = None
                            
                        if aml['main_group']:
                            main_group = str(aml['main_group']).strip()
                            cr.execute('select id from product_maingroup where lower(name) like %s', (main_group.lower(),))
                            main_group_ids = cr.fetchall()
                            if main_group_ids:
                                main_group_id = main_group_ids[0]
                            else:
                                main_group_id = maingroup_obj.create(cr, uid, {'name':main_group}, context=context)
                        else:
                            main_group_id = maingroup_obj.create(cr, uid, {'name':main_group}, context=context)
    
                        if aml['branch']:
                            branch = str(aml['branch']).strip()
                            cr.execute('select id from res_branch where lower(branch_code) like %s', (branch.lower(),))
                            branch_ids = cr.fetchall()
                            if branch_ids:
                                branch_id = branch_ids[0]
                            else:
                                branch_id = None
                        else:
                            branch = ''
                            branch_id = None
    
                        # Customer Code
                        if aml['customer_code']:
                            customer_code = str(aml['customer_code']).strip()
                            cr.execute('select id from res_partner where lower(customer_code) like %s', (customer_code.lower(),))
                            customer_ids = cr.fetchall()
                            if customer_ids:
                                customer_id = customer_ids[0]
                            else:
                                customer_id = None
                        else:
                            customer_code = ''
                            customer_id = None     
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
                        print 'day_plan>>>', day_plan
                        print 'sale_team_id>>>', sale_team_id
                        print 'date_data>>>', date_data
                        print 'principal_id>>>', principal_id
                        if day_plan and sale_team_id and date_data and principal_id:
                            cr.execute('select id from sale_plan_day where lower(name) like %s and sale_team= %s and date::date =%s ', (day_plan.lower(), sale_team_id, date_data,))
                            result = cr.fetchall()
                            if not result:
                                plan_id = sale_plan_day_obj.create(cr, uid, {'name': day_plan,
                                                                                            'sale_team':sale_team_id,
                                                                                            'date':date_data,
                                                                                            'principal':principal_id,
                                                                                            'active':True}, context=context)
                                if plan_id:
                                    # customer link
                                    cr.execute("select partner_id from res_partner_sale_plan_day_rel where sale_plan_day_id =%s ", (plan_id,))
                                    res_ids = cr.fetchall()
                                    if res_ids and customer_id:
                                        if customer_id not in res_ids:
                                            cr.execute("insert into res_partner_sale_plan_day_rel(sale_plan_day_id,partner_id) values(%s,%s)", (plan_id, customer_id,))
                                    elif not res_ids:
                                        if customer_id:
                                            cr.execute("insert into res_partner_sale_plan_day_rel(sale_plan_day_id,partner_id) values(%s,%s)", (plan_id, customer_id,))
                                    # main group link
                                    cr.execute("""select product_maingroup_id from product_maingroup_sale_plan_day_rel where sale_plan_day_id=%s""", (plan_id,))
                                    data = cr.fetchall()
                                    if data and main_group_id:
                                        if main_group_id not in data:
                                            cr.execute("insert into product_maingroup_sale_plan_day_rel(sale_plan_day_id,product_maingroup_id) values(%s,%s)", (plan_id, main_group_id,))
                                    elif not data:
                                        if main_group_id:
                                            cr.execute("insert into product_maingroup_sale_plan_day_rel(sale_plan_day_id,product_maingroup_id) values(%s,%s)", (plan_id, main_group_id,))
                            else:
                                plan_id = result[0][0]
                                cr.execute("select partner_id from res_partner_sale_plan_day_rel where sale_plan_day_id =%s ", (plan_id,))
                                res_ids = cr.fetchall()
                                if res_ids and customer_id:
                                    if customer_id not in res_ids:
                                        cr.execute("insert into res_partner_sale_plan_day_rel(sale_plan_day_id,partner_id) values(%s,%s)", (plan_id, customer_id,))
                                elif not res_ids:
                                    if customer_id:
                                        cr.execute("insert into res_partner_sale_plan_day_rel(sale_plan_day_id,partner_id) values(%s,%s)", (plan_id, customer_id,))
                                # main group link
                                cr.execute("""select product_maingroup_id from product_maingroup_sale_plan_day_rel where sale_plan_day_id=%s""", (plan_id,))
                                data = cr.fetchall()
                                if data and main_group_id:
                                    if main_group_id not in data:
                                        cr.execute("insert into product_maingroup_sale_plan_day_rel(sale_plan_day_id,product_maingroup_id) values(%s,%s)", (plan_id, main_group_id,))
                                elif not data:
                                    if main_group_id:
                                        cr.execute("insert into product_maingroup_sale_plan_day_rel(sale_plan_day_id,product_maingroup_id) values(%s,%s)", (plan_id, main_group_id,))
            except Exception, e:
                raise osv.except_osv(_('Warning!'), _('Something wrong with this %s .') % (e))                        
            self.write(cr, uid, ids, {'state':'completed'}, context=context)                       

    def import_sale_plan_trip(self, cr, uid, ids, context=None):

        sale_plan_day_obj = self.pool.get('sale.plan.trip')
        maingroup_obj = self.pool.get('product.maingroup')
        principal_obj = self.pool.get('product.principal')
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
                    day_plan_i = sale_team_i = customer_code_i = principal_i = main_group_i = date_i = branch_i = None
                    column_cnt = len(ln)
                    for i in range(column_cnt):
                        # header fields
                        header_field = ln[i].strip().lower()
                        if header_field not in header_fields:
                            err_log += '\n' + _("Invalid Excel File, Header Field '%s' is not supported !") % ln[i]
                        # required header fields : account, debit, credit
                        elif header_field == 'day':
                            day_plan_i = i
                        elif header_field == 'sale_team':
                            sale_team_i = i
                        elif header_field == 'customer_code':
                            customer_code_i = i
                        elif header_field == 'main_group':
                            main_group_i = i
                        elif header_field == 'date':
                            date_i = i
                        elif header_field == 'branch':
                            branch_i = i
                        elif header_field == 'principal':
                            principal_i = i
                    for f in [(principal_i, 'principal'), (day_plan_i, 'day'), (sale_team_i, 'sale_team'), (customer_code_i, 'customer_code'), (main_group_i, 'main_group'), (date_i, 'date'), (branch_i, 'branch')]:
                        if not isinstance(f[0], int):
                            err_log += '\n' + _("Invalid Excel file, Header '%s' is missing !") % f[1]
                        
                # process data lines   
            else:
                # add the without value for without header fields columns
                for i in range(0, val):
                    ln.append('')
                if ln and ln[0] and ln[0][0] not in ['#', '']:
                    import_vals = {}
                    import_vals['day'] = ln[day_plan_i]
                    import_vals['sale_team'] = ln[sale_team_i]
                    import_vals['customer_code'] = ln[customer_code_i]
                    import_vals['main_group'] = ln[main_group_i]
                    import_vals['date'] = ln[date_i]
                    import_vals['branch'] = ln[branch_i]
                    import_vals['principal'] = ln[principal_i]
                    amls.append(import_vals)
       
        if err_log:
            self.write(cr, uid, ids[0], {'note': err_log})
            self.write(cr, uid, ids[0], {'state': 'error'})
        if amls or err_log:
            print 'aml', amls
            try:
                for aml in amls:
                    principal_id = day_plan = sale_team = sale_team_id = customer_code = main_group = main_group_id = date = branch = branch_id = plan_id = customer_id = customer_code = None
                    data = None
                        
                    if aml['principal']:
                        principal = str(aml['principal']).strip()
                        principal = principal.replace(".0", "")
                        cr.execute("""select id from product_principal where lower(name) like %s """, (principal.lower(),))
                        data = cr.fetchall()
                        if data:
                            principal_id = data[0][0]
                        else:
                            principal_id = principal_obj.create(cr, uid, {'name':principal}, context=context)
                    
                    if aml['day']:
                        day_plan = str(aml['day']).strip()
                    else:
                        day_plan = None
                        
                    if aml['sale_team']:
                        sale_team = str(aml['sale_team']).strip()
                        cr.execute('select id from crm_case_section where lower(complete_name) like %s', (sale_team.lower(),))
                        sale_team_ids = cr.fetchall()
                        if sale_team_ids:
                            sale_team_id = sale_team_ids[0]
                        else:
                            sale_team_id = None
                    else:
                        sale_team = ''
                        
                    if aml['main_group']:
                        main_group = str(aml['main_group']).strip()
                        cr.execute('select id from product_maingroup where lower(name) like %s', (main_group.lower(),))
                        main_group_ids = cr.fetchall()
                        if main_group_ids:
                            main_group_id = main_group_ids[0]
                        else:
                            main_group_id = maingroup_obj.create(cr, uid, {'name':main_group}, context=context)
                    else:
                        main_group_id = maingroup_obj.create(cr, uid, {'name':main_group}, context=context)

                    if aml['branch']:
                        branch = str(aml['branch']).strip()
                        cr.execute('select id from res_branch where lower(branch_code) like %s', (branch.lower(),))
                        branch_ids = cr.fetchall()
                        if branch_ids:
                            branch_id = branch_ids[0]
                        else:
                            branch_id = None
                    else:
                        branch = ''
                        branch_id = None

                    # Customer Code
                    if aml['customer_code']:
                        customer_code = str(aml['customer_code']).strip()
                        cr.execute('select id from res_partner where lower(customer_code) like %s', (customer_code.lower(),))
                        customer_ids = cr.fetchall()
                        if customer_ids:
                            customer_id = customer_ids[0]
                        else:
                            customer_id = None
                    else:
                        customer_code = ''
                        customer_id = None     
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
                    
                    if day_plan and sale_team_id and date_data and principal_id:
                        cr.execute('select id from sale_plan_trip where lower(name) like %s and sale_team= %s and date::date =%s ', (day_plan.lower(), sale_team_id, date_data,))
                        result = cr.fetchall()
                        if not result:
                            plan_id = sale_plan_day_obj.create(cr, uid, {'name': day_plan,
                                                                                        'sale_team':sale_team_id,
                                                                                        'date':date_data,
                                                                                        'principal':principal_id,
                                                                                        'active':True}, context=context)
                            if plan_id:
                                cr.execute("select partner_id from res_partner_sale_plan_trip_rel where sale_plan_trip_id =%s ", (plan_id,))
                                res_ids = cr.fetchall()
                                if res_ids and customer_id:
                                    if customer_id not in res_ids:
                                        cr.execute("insert into res_partner_sale_plan_trip_rel(sale_plan_trip_id,partner_id) values(%s,%s)", (plan_id, customer_id,))
                                elif not res_ids:
                                    if customer_id:
                                        cr.execute("insert into res_partner_sale_plan_trip_rel(sale_plan_trip_id,partner_id) values(%s,%s)", (plan_id, customer_id,))
                                # main group link
                                cr.execute("""select product_maingroup_id from product_maingroup_sale_plan_day_reltrip where sale_plan_trip_id=%s""", (plan_id,))
                                data = cr.fetchall()
                                if data and main_group_id:
                                    if main_group_id not in data:
                                        cr.execute("insert into product_maingroup_sale_plan_day_reltrip(sale_plan_trip_id,product_maingroup_id) values(%s,%s)", (plan_id, main_group_id,))
                                elif not data:
                                    if main_group_id:
                                        cr.execute("insert into product_maingroup_sale_plan_day_reltrip(sale_plan_trip_id,product_maingroup_id) values(%s,%s)", (plan_id, main_group_id,))
                        else:
                            plan_id = result[0][0]
                            cr.execute("select partner_id from res_partner_sale_plan_trip_rel where sale_plan_trip_id =%s ", (plan_id,))
                            res_ids = cr.fetchall()
                            if res_ids and customer_id:
                                if customer_id not in res_ids:
                                    cr.execute("insert into res_partner_sale_plan_trip_rel(sale_plan_trip_id,partner_id) values(%s,%s)", (plan_id, customer_id,))
                            elif not res_ids:
                                if customer_id:
                                    cr.execute("insert into res_partner_sale_plan_trip_rel(sale_plan_trip_id,partner_id) values(%s,%s)", (plan_id, customer_id,))
                            # main group link
                            cr.execute("""select product_maingroup_id from product_maingroup_sale_plan_day_reltrip where sale_plan_trip_id=%s""", (plan_id,))
                            data = cr.fetchall()
                            if data and main_group_id:
                                if main_group_id not in data:
                                    cr.execute("insert into product_maingroup_sale_plan_day_reltrip(sale_plan_trip_id,product_maingroup_id) values(%s,%s)", (plan_id, main_group_id,))
                            elif not data:
                                if main_group_id:
                                    cr.execute("insert into product_maingroup_sale_plan_day_reltrip(sale_plan_trip_id,product_maingroup_id) values(%s,%s)", (plan_id, main_group_id,))
                                
                self.write(cr, uid, ids, {'state':'completed'}, context=context)                       
            except Exception, e:
                raise osv.except_osv(_('Warning!'), _('Something wrong with this %s .') % (e))    
