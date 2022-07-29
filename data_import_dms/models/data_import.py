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
import base64
import logging
from __builtin__ import True
_logger = logging.getLogger(__name__)
header_fields = ['principal', 'uom', 'name', 'category', 'public_price', 'default_code', 'bar_code', 'product_type', 'division', 'group', 'main_group', 'description', 'costing_method', 'cost_price', 'inventory_valuation', 'full_lots_traceability', 'track_incoming_lots', 'track_outgoing_lots']

class product(osv.osv):
    _name = 'data_import.product'
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
    
    _constraints = [(_check_file_ext, "Please import Excel file!", ['import_fname'])]
    
    def import_data(self, cr, uid, ids, context=None):
        product_template_obj = self.pool.get('product.template')
        product_brand_obj = self.pool.get('product.brand')
        product_api_obj = self.pool.get('product.api')
        product_division_obj = self.pool.get('product.division')
        product_group_obj = self.pool.get('product.group')
        product_maingroup_obj = self.pool.get('product.maingroup')
        uom_obj = self.pool.get('product.uom')
        category_obj = self.pool.get('product.category')
        principal_obj = self.pool.get('product.principal')
        
        # #taking the parent categ_id from product_category table
        
        cr.execute('select id from product_category where lower(name) like %s', ('all',))
        parent_cat_id = cr.fetchall()
        # print 'this is parent_category id',parent_cat_id
        if parent_cat_id:
            parent_cat_id = parent_cat_id[0][0]
        else:
            value = {'name':'All'}
            category_obj.create(cr, uid, value, context=None)
            cr.execute('select id from product_category where lower(name) like %s', ('all',))
            parent_cat_id = cr.fetchone()[0]
        cr.execute('select id from product_category where lower(name) like %s', ('saleable',))
        saleable = cr.fetchall()
        if not saleable:
            val = {'name':'Saleable',
                 'parent_id':parent_cat_id}
            category_obj.create(cr, uid, val, context=None)
        else:
            val = {'parent_id':parent_cat_id}
            category_obj.write(cr, uid, saleable[0], val)
            
        ir_model_fields_obj = self.pool.get('ir.model.fields')
        ir_property_obj = self.pool.get('ir.property')
        data = self.browse(cr, uid, ids)[0]
        company_id = data.company_id.id
        import_file = data.import_file
        import_filename = data.name

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
                    principal_i = product_type_i = uom_i = name_i = category_i = public_price_i = default_code_i = bar_code_i = division_i = group_i = main_group_i = description_i = costing_method_i = cost_price_i = inventory_valuation_i = flt_i = til_i = tol_i = None
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
                        header_field = ln[i].strip().lower()
                        if header_field not in header_fields:
                            err_log += '\n' + _("Invalid EXCEL File, Header Field '%s' is not supported !") % ln[i]
                        # required header fields : account, debit, credit         
                        elif header_field == 'principal':
                            principal_i = i
                        elif header_field == 'uom':
                            uom_i = i
                        elif header_field == 'description':
                            description_i = i
                        elif header_field == 'name':
                            name_i = i
                        elif header_field == 'category':
                            category_i = i
                        elif header_field == 'public_price':
                            public_price_i = i
                        elif header_field == 'default_code':
                            default_code_i = i
                        elif header_field == 'bar_code':
                            bar_code_i = i
                        elif header_field == 'division':
                            division_i = i
                        elif header_field == 'group':
                            group_i = i
                        elif header_field == 'main_group':
                            main_group_i = i
                        elif header_field == 'product_type':
                            product_type_i = i
                        elif header_field == 'costing_method':
                            costing_method_i = i
                        elif header_field == 'cost_price':
                            cost_price_i = i
                        elif header_field == 'inventory_valuation':
                            inventory_valuation_i = i
                        elif header_field == 'full_lots_traceability':
                            flt_i = i
                        elif header_field == 'track_incoming_lots':
                            til_i = i
                        elif header_field == 'track_outgoing_lots':
                            tol_i = i     

                    for f in [(principal_i, 'principal'), (costing_method_i, 'costing_method'), (cost_price_i, 'cost_price'), (inventory_valuation_i, 'inventory_valuation'), (flt_i, 'full_lots_traceability'), (til_i, 'track_incoming_lots'), (tol_i, 'track_outgoing_lots'), (product_type_i, 'product_type'), (uom_i, 'uom'), (name_i, 'name'), (category_i, 'category'), (public_price_i , 'public_price'), (default_code_i, 'default_code'), (bar_code_i, 'bar_code'), (division_i, 'division'), (group_i, 'group'), (main_group_i, 'main_group')]:
                        if not isinstance(f[0], int):
                            err_log += '\n' + _("Invalid CSV file, Header '%s' is missing !") % f[1]
                        
                # process data lines   
            else:
                # add the without value for without header fields columns
                for i in range(0, val):
                    ln.append('')
                if ln and ln[0] and ln[0][0] not in ['#', '']:
                    
                    import_vals = {}
                    import_vals['uom'] = ln[uom_i]
                    import_vals['name'] = ln[name_i]
                    import_vals['description'] = ln[description_i]
                    import_vals['category'] = ln[category_i]
                    import_vals['public_price'] = ln[public_price_i]
                    import_vals['default_code'] = ln[default_code_i]
                    import_vals['bar_code'] = ln[bar_code_i]
                    import_vals['division'] = ln[division_i]
                    import_vals['group'] = ln[group_i]
                    import_vals['main_group'] = ln[main_group_i]
                    import_vals['product_type'] = ln[product_type_i]
                    import_vals['costing_method'] = ln[costing_method_i]
                    import_vals['cost_price'] = ln[cost_price_i]
                    import_vals['inventory_valuation'] = ln[inventory_valuation_i]
                    import_vals['full_lots_traceability'] = ln[flt_i]
                    import_vals['track_incoming_lots'] = ln[til_i]
                    import_vals['track_outgoing_lots'] = ln[tol_i]
                    import_vals['principal'] = ln[principal_i]
                    amls.append(import_vals)
                  
        if err_log:
            self.write(cr, uid, ids[0], {'note': err_log})
            self.write(cr, uid, ids[0], {'state': 'error'})
        else:
            for aml in amls:
                try:
                    main_group_ids = group_ids = division_ids = cat_ids = uom_ids = principal_id = iv_ids = s_ids = r_ids = a_ids = uom_id = description = product_name = category_id = product_id = division_id = group_id = main_group_id = fields_id = costing_method = inventory_valuation = flt = til = tol = None
                    value = {}
                    cat_name = uom_name = division_name = group_name = main_group_name = default_code = principal = bar_code = product_type = None
                    if aml['category']:
                        cat_name = str(aml['category']).strip()
                    
                    if aml['uom']:
                        uom_name = str(aml['uom']).strip()
                        
                    if aml['division']:
                        division_name = str(aml['division']).strip()
                        
                    if aml['group']:
                        group_name = str(aml['group']).strip()
                        
                    if aml['main_group']:
                        main_group_name = str(aml['main_group']).strip()
                        
                    if aml['default_code']:
                        default_code = str(aml['default_code']).strip()
                        
                    if aml['principal']:
                        principal = str(aml['principal']).strip()
                        
                    if aml['bar_code']:
                        bar_code = aml['bar_code'].strip()
                        
                    if aml['product_type']:
                        product_type = str(aml['product_type']).strip()
                    
                    if principal:
                        principal = principal.strip()
                        principal = principal.replace('.0', '')
                        cr.execute("""select id from product_principal where lower(name) like %s""", (principal.lower(),))
                        principal_val = {'name':principal}
                        data = cr.fetchall()
                        if data:
                            principal_id = data[0][0]
                        else:
                            principal_id = principal_obj.create(cr, uid, principal_val, context=context)
                            
                    if bar_code:
                        bar_code = bar_code.strip()
                        bar_code = bar_code.replace('.0', '')
                        
                    if default_code:
                        default_code = default_code.strip()
                        default_code = default_code.replace('.0', '')
                        
                    if main_group_name:
                        main_group_name = main_group_name.strip()
                        
                    if group_name:
                        group_name = group_name.strip()
                        
                    if division_name:
                        division_name = division_name.strip()
                        
                    if uom_name:
                        uom_name = uom_name.strip()
                        
                    if cat_name:
                        cat_name = cat_name.strip()   
                        
                    if aml['name']:
                        product_name = aml['name'].replace(',', ' ')
                        
                    if aml['description']:
                        description = aml['description'].replace(',', ' ')
                        
                    if aml['costing_method']:
                        costing_method = str(aml['costing_method']).strip()
                    else:
                        costing_method = None
                        
                    
                    if aml['cost_price']:
                        cost_price = float(aml['cost_price'])
                    else:
                        cost_price = 0.0
                    
                    if aml['inventory_valuation']:
                        inventory_valuation = str(aml['inventory_valuation']).strip()
                    else:
                        inventory_valuation = None
                        
                    
                    if aml['full_lots_traceability']:
                        full_lots_traceability = str(aml['full_lots_traceability']).strip()
                    else:
                        full_lots_traceability = None
                        
                    
                    if aml['track_incoming_lots']:
                        track_incoming_lots = str(aml['track_incoming_lots']).strip()
                    else:
                        track_incoming_lots = None
                        
                    
                    if aml['track_outgoing_lots']:
                        track_outgoing_lots = str(aml['track_outgoing_lots']).strip()
                    else:
                        track_outgoing_lots = None
                        
                    
                    if uom_name:
                        
                        cr.execute("""select id from product_uom where lower(name) = %s """ , (uom_name.lower(),))
                        data = cr.fetchall()
                        if data: 
                            uom_ids = data[0][0]
                            
                        if not uom_ids:
                            uom_value = {
                                      'name':uom_name,
                                      'category_id':1,  # unit
                                      'factor': 1,
                                      'active': True,
                                      'uom_type': 'bigger',
                                      }
                            uom_id = uom_obj.create(cr, uid, uom_value, context)
                        else:
                            uom_id = uom_ids            
                    # Right to Here#
                    if cat_name:
                        
                        cr.execute("""select id from product_category where lower(name) = %s """, (cat_name.lower(),))
                        data = cr.fetchall()
                        if data:
                            cat_ids = data[0][0]
                            
                        if not cat_ids:
                            cat_value = {
                                       'name':cat_name,
                                       'type':'normal',
                                       'parent_id':parent_cat_id
                                       }
                            category_id = category_obj.create(cr, uid, cat_value, context)    
                        else:
                            category_id = cat_ids       
                            
                    if division_name:
                        
                        cr.execute("""select id from product_division where lower(name)= %s """, (division_name.lower(),))
                        data = cr.fetchall()
                        if data:
                            division_ids = data[0][0]
                        if not division_ids:
                            division_value = {
                                      'name':division_name,
                                      }
                            division_id = product_division_obj.create(cr, uid, division_value, context)
                        else:
                            division_id = division_ids                
                            
                    if group_name:
                        
                        cr.execute(""" select id from product_group where  lower(name) = %s """ , (group_name.lower(),))
                        data = cr.fetchall()
                        if data:
                            group_ids = data[0][0]
                        if not group_ids:
                            group_value = {
                                       'name':group_name,
                                       }
                            group_id = product_group_obj.create(cr, uid, group_value, context)
                        else:
                            group_id = group_ids      
                                    
                    
                    if main_group_name:
                        
                        cr.execute("""select id from product_maingroup where lower(name) = %s """, (main_group_name.lower(),))
                        data = cr.fetchall()
                        if data:
                            main_group_ids = data[0][0]
                            
                        if not main_group_ids:
                            maingroup_value = {
                                       'name':main_group_name,
                                       }
                            main_group_id = product_maingroup_obj.create(cr, uid, maingroup_value, context)
                        else:
                            main_group_id = main_group_ids   
    
                        
                    if product_type:
                        if product_type == 'stockable product' or product_type == 'product':
                            value = {
                                   'type':'product'}
                        elif product_type == 'consumable' or product_type == 'consumable product':
                            value = {
                                   'type':'consu'}
                        elif product_type == 'service':
                            value = {
                                   'type':'service'}       
                        
                    if full_lots_traceability:
                        if full_lots_traceability.lower() == 'true' or full_lots_traceability.lower() == '1':
                            flt = True
                        elif full_lots_traceability.lower() == 'false' or full_lots_traceability.lower() == '0':
                            flt = False
                    
                    if track_incoming_lots:
                        if track_incoming_lots.lower() == 'true' or track_incoming_lots.lower() == '1':
                            til = True
                        elif track_incoming_lots.lower() == 'false' or track_incoming_lots.lower() == '0':
                            til = False
                    
                    if track_outgoing_lots:
                        if track_outgoing_lots.lower() == 'true' or track_outgoing_lots.lower() == '1':
                            tol = True
                        elif track_outgoing_lots.lower() == 'false' or track_outgoing_lots.lower() == '0':
                            tol = False
                        
                    value = {
                             'uom_id':uom_id,
                             'uom_po_id':uom_id,
                             'name':product_name,
                             'categ_id':category_id,
                             'list_price':aml['public_price'],
                             'default_code':default_code,
                             'division':division_id,
                             'group':group_id,
                             'main_group':main_group_id,
                             'type':'product',
                             'description':description,
                             'barcode_no':bar_code,
                             'track_all':flt,
                             'track_incoming':til,
                             'track_outgoing':tol,
                             'product_principal_ids':principal_id
                             }
                    
                    product_ids = product_template_obj.search(cr, uid, [('default_code', '=', default_code)
                                                                     ])
                    if not product_ids:
                        product_id = product_template_obj.create(cr, uid, value, context=context)
                    else:
                        product_id = product_template_obj.write(cr, uid, product_ids[0], value)
                        product_id = product_ids[0]
                    
                    res_id = 'product.template,'
                    res_id += str(product_id)
                    con = None
                    
                    if product_id:
                        if uom_id:
                            cr.execute('select product_template_id from product_template_product_uom_rel where product_template_id = %s and product_uom_id = %s', (product_id, uom_id,))
                            con = cr.fetchall()
                            if len(con) <= 0:
                                cr.execute('insert into product_template_product_uom_rel(product_template_id,product_uom_id) values(%s,%s)', (product_id, uom_id,))
                                
                        if costing_method:  # may be standard price, may be real price, may be average price
                            if costing_method.lower() == 'standard price':
                                fields_id = ir_model_fields_obj.search(cr, uid, [('name', '=', 'standard_price'), ('model', '=', 'product.template')])
                                if fields_id:
                                    res = {'name':'standard_price',
                                         'res_id':res_id,
                                         'value_float':cost_price,
                                         'type':'float',
                                         'fields_id':fields_id[0],
                                         'company_id':company_id}
                                    s_ids = ir_property_obj.search(cr, uid, ['&', ('res_id', '=', res_id), ('name', '=', 'standard_price'), ('fields_id', '=', fields_id[0])])
                                    if not s_ids:
                                        ir_property_obj.create(cr, uid, res, context)
                                    else:
                                        ir_property_obj.write(cr, uid, s_ids[0], res)
                                     
                            elif costing_method.lower() == 'real price':
                                fields_id = ir_model_fields_obj.search(cr, uid, [('name', '=', 'standard_price'), ('model', '=', 'product.template')])
                                if fields_id:
                                    res = {'name':'standard_price',
                                         'res_id':res_id,
                                         'value_float':cost_price,
                                         'type':'float',
                                         'fields_id':fields_id[0]
                                       , 'company_id':company_id}
                                    s_ids = ir_property_obj.search(cr, uid, ['&', ('res_id', '=', res_id), ('name', '=', 'standard_price'), ('fields_id', '=', fields_id[0])])
                                    if not s_ids:
                                        ir_property_obj.create(cr, uid, res, context)
                                    else:
                                        ir_property_obj.write(cr, uid, s_ids[0], res, context=context)
                                fields_id = ir_model_fields_obj.search(cr, uid, [('name', '=', 'cost_method'), ('model', '=', 'product.template')])
                                
                                if fields_id:
                                    res = {'name':'cost_method',
                                           'value_text':'real',
                                           'type':'selection',
                                           'fields_id':fields_id[0],
                                           'res_id':res_id
                                         , 'company_id':company_id}
                                    r_ids = ir_property_obj.search(cr, uid, ['&', ('res_id', '=', res_id), ('name', '=', 'cost_method'), ('fields_id', '=', fields_id[0]), ('value_text', '=', 'real')])
                                    if not r_ids:
                                        ir_property_obj.create(cr, uid, res, context)
                                    else:
                                        ir_property_obj.write(cr, uid, r_ids[0], res, context=context)     
                                        
                            elif costing_method.lower() == 'average price':
                                fields_id = ir_model_fields_obj.search(cr, uid, [('name', '=', 'standard_price'), ('model', '=', 'product.template')])
                                if fields_id:
                                    res = {'name':'standard_price',
                                         'res_id':res_id,
                                         'value_float':cost_price,
                                         'type':'float',
                                         'fields_id':fields_id[0]
                                       , 'company_id':company_id}
                                    s_ids = ir_property_obj.search(cr, uid, ['&', ('res_id', '=', res_id), ('name', '=', 'standard_price'), ('fields_id', '=', fields_id[0])])
                                    if not s_ids:
                                        ir_property_obj.create(cr, uid, res, context)
                                    else:
                                        ir_property_obj.write(cr, uid, s_ids[0], res)
                                        
                                fields_id = ir_model_fields_obj.search(cr, uid, [('name', '=', 'cost_method'), ('model', '=', 'product.template')])
                                if fields_id:
                                    res = {'name':'cost_method',
                                           'value_text':'average',
                                           'type':'selection',
                                           'fields_id':fields_id[0],
                                           'res_id':res_id
                                         , 'company_id':company_id}
                                    
                                    a_ids = ir_property_obj.search(cr, uid, ['&', ('res_id', '=', res_id), ('name', '=', 'cost_method'), ('fields_id', '=', fields_id[0]), ('value_text', '=', 'average')])
                                    
                                    if not a_ids:
                                        ir_property_obj.create(cr, uid, res, context)
                                    else:
                                        ir_property_obj.write(cr, uid, a_ids[0], res, context=context)       
                         
                        if inventory_valuation:
                            if inventory_valuation.lower() == 'automated':
                                fields_id = ir_model_fields_obj.search(cr, uid, ['&', ('name', '=', 'valuation'), ('model', '=', 'product.template')])
                                if fields_id:
                                    res = {'name':'valuation',
                                         'res_id':res_id,
                                         'value_text':'real_time',
                                         'type':'selection',
                                         'fields_id':fields_id[0]
                                       , 'company_id':company_id}
                                    iv_ids = ir_property_obj.search(cr, uid, ['&', ('res_id', '=', res_id), ('name', '=', 'valuation'), ('fields_id', '=', fields_id[0]), ('value_text', '=', 'real_time')])
                                    if not iv_ids:
                                        ir_property_obj.create(cr, uid, res, context)
                                    else:
                                        ir_property_obj.write(cr, uid, iv_ids[0], res, context=context)     
                                        
                            else:
                                fields_id = ir_model_fields_obj.search(cr, uid, ['&', ('name', '=', 'valuation'), ('model', '=', 'product.template')])
                                iv_ids = ir_property_obj.search(cr, uid, ['&', ('res_id', '=', res_id), ('name', '=', 'valuation'), ('fields_id', '=', fields_id[0]), ('value_text', '=', 'real_time')])
                                 
                                if iv_ids:
                                     
                                    if len(iv_ids) > 1:
                                        for ids in iv_ids:
                                            cr.execute('delete from ir_property where id = %s', (ids,))       
                                    else:              
                                        cr.execute('delete from ir_property where id = %s', (iv_ids[0],))                        
                except Exception, e:
                    raise osv.except_osv(
                        _('Cannot Import Excel Data!'),
                        _('Something Wrong with Excel Data!\n %s') % (e))
                
                    
            self.write(cr, uid, ids[0], {'state': 'completed'})
                    
                        
                            


        
