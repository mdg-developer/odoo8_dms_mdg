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
_logger = logging.getLogger(__name__)
header_fields = ['uom', 'name','category','standard_price','public_price','default_code','bar_code','product_type','division','group','main_group','description']

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
    
    _constraints = [(_check_file_ext,"Please import Excel file!",['import_fname'])]
    
    def import_data(self, cr, uid, ids, context=None):
        product_template_obj = self.pool.get('product.template')
        product_brand_obj = self.pool.get('product.brand')
        product_api_obj = self.pool.get('product.api')
        product_division_obj = self.pool.get('product.division')
        product_group_obj = self.pool.get('product.group')
        product_maingroup_obj = self.pool.get('product.maingroup')
        uom_obj = self.pool.get('product.uom')
        category_obj = self.pool.get('product.category')
        
        ##taking the parent categ_id from product_category table
        
        cr.execute('select id from product_category where lower(name) like %s',('all',))
        parent_cat_id = cr.fetchall()
        #print 'this is parent_category id',parent_cat_id
        if parent_cat_id:
            parent_cat_id=parent_cat_id[0]
        else:
            value={'name':'All'}
            category_obj.create(cr,uid,value,context=None)
            cr.execute('select id from product_category where lower(name) like %s',('all',))
            parent_cat_id = cr.fetchone()[0]
        cr.execute('select id from product_category where lower(name) like %s',('saleable',))
        saleable=cr.fetchall()
        if not saleable:
            val={'name':'Saleable',
                 'parent_id':parent_cat_id}
            category_obj.create(cr,uid,val,context=None)
        else:
            val={'parent_id':parent_cat_id}
            category_obj.write(cr,uid,saleable[0],val)
            
        ir_model_fields_obj=self.pool.get('ir.model.fields')
        ir_property_obj = self.pool.get('ir.property')
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
                    raise orm.except_orm(_('Error :'), _("Error while processing the header line %s. \n\nPlease check your Excel separator as well as the column header fields") %ln)
                else:
                    header_line = True
                    product_type_i = uom_i = name_i = category_i = standard_price_i = public_price_i = default_code_i = bar_code_i = division_i = group_i = main_group_i = description_i = None
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
                        elif header_field == 'uom':
                            uom_i = i
                        elif header_field == 'description':
                            description_i=i
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
                        elif header_field == 'standard_price':
                            standard_price_i =i
                            
                    for f in [(standard_price_i,'standard_price'),(product_type_i,'product_type'),(uom_i,'uom'),(name_i,'name'),(category_i,'category'),(public_price_i ,'public_price'),(default_code_i,'default_code'),(bar_code_i,'bar_code'),(division_i,'division'),(group_i,'group'),(main_group_i,'main_group')]:
                        if not isinstance(f[0],int):
                            err_log += '\n'+ _("Invalid CSV file, Header '%s' is missing !") % f[1]
                        
                #process data lines   
            else:
                if ln and ln[0] and ln[0][0] not in ['#','']:
                    
                    import_vals = {}
                    import_vals['uom'] =  ln[uom_i]
                    import_vals['name'] = ln[name_i].strip()
                    import_vals['category'] = ln[category_i]
                    import_vals['public_price'] = ln[public_price_i]
                    import_vals['default_code'] = ln[default_code_i].strip()
                    import_vals['bar_code'] = ln[bar_code_i]
                    import_vals['division'] = ln[division_i]
                    import_vals['group'] = ln[group_i]
                    import_vals['main_group']=ln[main_group_i]
                    import_vals['product_type']=ln[product_type_i]
                    import_vals['standard_price']=ln[standard_price_i]
                    import_vals['description']=ln[description_i].strip()
                                    
                    amls.append(import_vals)
                  
        if err_log:
            self.write(cr, uid, ids[0], {'note': err_log})
            self.write(cr, uid, ids[0], {'state': 'failed'})
        else:
            for aml in amls:
                uom_id = category_id = product_id = division_id = group_id = main_group_id = fields_id = None
                cat_name = aml['category']
                uom_name = aml['uom']
                division_name = aml['division']
                group_name = aml['group']
                main_group_name = aml['main_group']
                product_name = aml['name']
                bar_code=str(aml['bar_code'])
                product_type=aml['product_type'].lower()
                standard_price=aml['standard_price']
                if uom_name:
                    uom_ids = uom_obj.search(cr,uid,[('name','=',uom_name)])
                    if not uom_ids:
                        uom_value={
                                  'name':uom_name,
                                  'category_id':1,#unit
                                  'factor': 1,
                                  'active': True,
                                  'uom_type': 'bigger',
                                  }
                        uom_id = uom_obj.create(cr,uid,uom_value, context)
                    else:
                        uom_id = uom_ids[0]                    
                if cat_name:
                    cat_ids = category_obj.search(cr,uid,[('name','=',cat_name)])
                    if not cat_ids:
                        cat_value={
                                   'name':cat_name,
                                   'type':'normal',
                                   'parent_id':parent_cat_id
                                   }
                        category_id = category_obj.create(cr,uid,cat_value,context)
                    else:
                        category_id = cat_ids[0]
                if division_name:
                    division_ids = product_division_obj.search(cr,uid,[('name','=',division_name)])
                    if not division_ids:
                        division_value={
                                  'name':division_name,
                                  }
                        division_id = product_division_obj.create(cr,uid,division_value, context)
                    else:
                        division_id = division_ids[0]
                        
                if group_name:
                    group_ids = product_group_obj.search(cr,uid,[('name','=',group_name)])
                    if not group_ids:
                        group_value={
                                   'name':group_name,
                                   }
                        group_id = product_group_obj.create(cr,uid,group_value,context)
                    else:
                        group_id = group_ids[0]      
                if main_group_name:
                    main_group_ids = product_maingroup_obj.search(cr,uid,[('name','=',main_group_name)])
                    if not main_group_ids:
                        maingroup_value={
                                   'name':main_group_name,
                                   }
                        main_group_id = product_maingroup_obj.create(cr,uid,maingroup_value,context)
                    else:
                        main_group_id = main_group_ids[0] 

                        
                    
                if product_type:
                    if product_type=='stockable product' or product_type=='product':
                        value={
                               'type':'product'}
                    elif product_type=='consumable' or product_type=='consumable product':
                        value={
                               'type':'consu'}
                    elif product_type=='service':
                        value={
                               'type':'service'}
                    value = {
                             'uom_id':uom_id,
                             'name':product_name,
                             'categ_id':category_id,
                             'list_price':aml['public_price'],
                             'default_code':aml['default_code'],
                             'division':division_id,
                             'group':group_id,
                             'main_group':main_group_id,
                             'type':'product',
                             'description':aml['description'],
                             'barcode_no':aml['bar_code']
                             }
                    if len(bar_code) == 13: 
                        value['ean13'] = aml['bar_code']
                product_ids = product_template_obj.search(cr,uid,[('default_code','=',aml['default_code'])
                                                                 ])
                
                if not product_ids:
                    product_id=product_template_obj.create(cr, uid, value, context=context)
                else:
                    product_id=product_template_obj.write(cr,uid,product_ids[0],value)
                print product_id    
                res_id='product.template,'
                res_id+=str(product_id)
                if product_id:
                    if standard_price:
                        fields_id =ir_model_fields_obj.search(cr,uid,[('name','=','standard_price')])
                        if fields_id:
                            res={'res_id':res_id,
                                 'value_float':standard_price,
                                 'type':'float',
                                 'fields_id':fields_id[0]}
                            ir_property_obj.create(cr,uid,res,context)
                            print 'this is product.template standard_price',standard_price
            self.write(cr, uid, ids[0], {'state': 'completed'})
        print amls
                    
                        
                            


        
