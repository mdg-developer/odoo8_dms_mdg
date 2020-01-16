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
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)
header_fields = ['default_code', 'product_name', 'public_price', 'uom', 'balance_qty', 'cost_price']

class sl_import(orm.TransientModel):
    _name = 'stock.line.import'
    _description = 'Import inventory adjust product lines'
    _columns = {
        'sl_data': fields.binary('File', required=True),
        'sl_fname': fields.char('Filename', size=128, required=True),
        'note':fields.text('Log'),
    }
    _defaults = {
        'sl_fname': '',
    }
    
    def _check_file_ext(self, cursor, user, ids):
        for import_file in self.browse(cursor, user, ids):
            if '.xls' in import_file.import_fname:return True
            else: return False
        return True
    
    _constraints = [(_check_file_ext, "Please import Excel file!", ['import_fname'])]

    def get_product_from_inventory(self, cr, uid, from_location, context=None):
        location_obj = self.pool.get('stock.location')
        product_obj = self.pool.get('product.product')
        location_ids = location_obj.search(cr, uid, [('id', 'child_of', [from_location])], context=context)
        domain = ' location_id in %s'
        args = (tuple(location_ids),)
        cr.execute('''
           SELECT product_id, sum(qty) as product_qty, location_id, lot_id as prod_lot_id, package_id, owner_id as partner_id
           FROM stock_quant WHERE''' + domain + '''
           GROUP BY product_id, location_id, lot_id, package_id, partner_id
        ''', args)
        vals = []
        for product_line in cr.dictfetchall():
            # replace the None the dictionary by False, because falsy values are tested later on
            for key, value in product_line.items():
                if not value:
                    product_line[key] = False
            # product_line['inventory_id'] = inventory.id
            product_line['theoretical_qty'] = product_line['product_qty']
            if product_line['product_id']:
                product = product_obj.browse(cr, uid, product_line['product_id'], context=context)
                product_line['product_uom_id'] = product.uom_id.id
            vals.append(product_line)
        return vals   
    
  
    def excel_import(self, cr, uid, ids, context=None):
        
        uom_obj = self.pool.get('product.uom')
        product_template_obj = self.pool.get('product.template')
        fields_obj = self.pool.get('ir.model.fields')
        property_obj = self.pool.get('ir.property')
        stock_move_line_obj = self.pool.get('stock.inventory.line')
        company_id = context['company_id']
        move_id = context['move_id']

        location_id = context['location_id']
        data = self.browse(cr, uid, ids)[0]
        import_file = data.sl_data
        # print 'file',data.sl_data
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
        amls = []
        count = val = head_count = 0
        for ln in excel_rows:
            if not ln :
                continue
            if not header_line:
                for l in header_fields:
                    if str(l).strip().lower() in [str(x).strip().lower() for x in ln]:
                        head_count = head_count + 1
                if head_count < 1:
                    print 'Illegal Header Fields'
                
                else:
                    if ln:
                        for l in header_fields:
                            if str(l).strip() in [str(x).strip().lower() for x in ln]:
                                print 'same fields', l
                            else:
                                # check the columns without contained the header fields
                                ln.append(str(l))
                                count = count + 1
                                val = count     
                    header_line = True
                    default_code_i = product_name_i = public_price_i = uom_i = balance_qty_i = cost_price_i = None
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
                            err_log += '\n' + _("Invalid CSV File, Header Field '%s' is not supported !") % ln[i]
                        # required header fields : account, debit, credit
                        elif header_field == 'default_code':
                            default_code_i = i
                        elif header_field == 'product_name':
                            product_name_i = i
                        elif header_field == 'uom':
                            uom_i = i
                        elif header_field == 'balance_qty':
                            balance_qty_i = i
                        elif header_field == 'cost_price':
                            cost_price_i = i
                        elif header_field == 'public_price':
                            public_price_i = i
                    for f in [(default_code_i, 'default_code'), (public_price_i, 'public_price'), (uom_i, 'uom'), (product_name_i, 'product_name'), (balance_qty_i, 'balance_qty'), (cost_price_i, 'cost_price')]:
                        if not isinstance(f[0], int):
                            err_log += '\n' + _("Invalid CSV file, Header '%s' is missing !") % f[1]
                         
                # process data lines   
            else:
                # add the without value for without header fields columns
                for i in range(0, val):
                    ln.append('')
                if ln and ln[0]:
                     
                    import_vals = {}
                    if default_code_i > -1: 
                        import_vals['default_code'] = ln[default_code_i]
                    if uom_i > -1: 
                        import_vals['uom'] = ln[uom_i]
                    if product_name_i > -1: 
                        import_vals['product_name'] = ln[product_name_i]
                    if public_price_i > -1: 
                        import_vals['public_price'] = ln[public_price_i]
                    if balance_qty_i > -1: 
                        import_vals['balance_qty'] = ln[balance_qty_i]
                    if cost_price_i > -1: 
                        import_vals['cost_price'] = ln[cost_price_i]
                    amls.append(import_vals)
                   
        if err_log:
            self.write(cr, uid, ids[0], {'note': err_log})
            self.write(cr, uid, ids[0], {'state': 'failed'})
        else:
            for aml in amls:
                default_code = uom_ids = uom_id = product_id = product_template_id = uom_name = product_name = product_qty = price = public_price = None
                value = []
                if aml['default_code']:
                    default_code = str(aml['default_code']).strip()
                    
                if aml['uom']:
                    uom_name = str(aml['uom']).strip()
                else:
                    uom_name = 'Unit(s)'  # default uom
                if aml['product_name']:
                    product_name = str(aml['product_name']).strip()
                    
                if aml['balance_qty']:
                    product_qty = aml['balance_qty']
                    
                if aml['cost_price']:
                    price = aml['cost_price']
                    
                if aml['public_price']:
                    public_price = aml['public_price']
                    
                if uom_name:
                    uom_id = uom_obj.search(cr, uid, [('name', '=', uom_name)])
                    if not uom_id:
                        raise osv.except_osv(_('Error!'), _("UOM is not exist!"))
                        uom_ids = 'not contain'
                    else:
                        uom_ids = uom_id[0]
                        # print uom_ids
                if  product_name:    
                    cr.execute("""select id from product_product where name_template= %s """, (product_name,))
                    data = cr.fetchall()
                    if data:
                        product_id = data[0][0]
                    else:
                        raise Warning(_('This Product %s  is not present in the system') % product_name)       
                    if product_id:
                        cr.execute('select product_tmpl_id from product_product where id = %s', (product_id,))
                        product_template_id = cr.fetchone()
                        if uom_ids and product_id:
                            print 'inventory_id', move_id
                        if move_id:
                            cr.execute('select id from stock_inventory_line where inventory_id = %s and product_id = %s', (move_id, product_id,))
                            
                            exist = cr.fetchone()
                            # print 'exist ',exist
                            if not exist:
                                value = {'inventory_id':move_id, 'product_uom_id':uom_ids, 'product_id':product_id, 'location_id':location_id, 'product_qty':product_qty, 'product_name':product_name}
                                stock_move_line_obj.create(cr, uid, value, context=context)
                            else:
                                value = {'product_qty':product_qty}
                                stock_move_line_obj.write(cr, uid, exist, value)
                            res_id = 'product.template,'
                            res_id += str(product_template_id[0])
                            if product_template_id:
                                product_template_obj.write(cr, uid, product_template_id, {'list_price':public_price})
                                if price:
                                    standard_field_id = fields_obj.search(cr, uid, [('name', '=', 'standard_price')])
                                    if standard_field_id:
                                        # print 'standard_field',standard_field_id[0]
                                        res = {'res_id':res_id,
                                             'value_float':price,
                                             'type':'float',
                                             'company_id':company_id,
                                             'fields_id':standard_field_id[0]}
                                        property_obj.create(cr, uid, res, context)  
                if default_code:
                    cr.execute("""select id from product_product where lower(default_code) like %s """, (default_code.lower(),))
                    data = cr.fetchall()
                    if data:
                        product_id = data[0][0]
                    else:
                        product_id = None
                    if product_id:
                        cr.execute('select product_tmpl_id from product_product where id = %s', (product_id,))
                        product_template_id = cr.fetchone()
                        if uom_ids and product_id:
                            print 'inventory_id', move_id
                        if move_id:
                            cr.execute('select id from stock_inventory_line where inventory_id = %s and product_id = %s', (move_id, product_id,))
                            
                            exist = cr.fetchone()
                            # print 'exist ',exist
                            if not exist:
                                value = {'inventory_id':move_id, 'product_uom_id':uom_ids, 'product_id':product_id, 'location_id':location_id, 'product_qty':product_qty, 'product_name':product_name}
                                stock_move_line_obj.create(cr, uid, value, context=context)
                            else:
                                value = {'product_qty':product_qty}
                                stock_move_line_obj.write(cr, uid, exist, value)
                            res_id = 'product.template,'
                            res_id += str(product_template_id[0])
                            if product_template_id:
                                product_template_obj.write(cr, uid, product_template_id, {'list_price':public_price})
                                if price:
                                    standard_field_id = fields_obj.search(cr, uid, [('name', '=', 'standard_price')])
                                    if standard_field_id:
                                        # print 'standard_field',standard_field_id[0]
                                        res = {'res_id':res_id,
                                             'value_float':price,
                                             'type':'float',
                                             'company_id':company_id,
                                             'fields_id':standard_field_id[0]}
                                        property_obj.create(cr, uid, res, context)
                                        # print 'this is product.template standard_price',price 
                        
                    
                
            self.write(cr, uid, ids[0], {'state': 'completed'})
        print 'this is aml', amls
                     
                         
