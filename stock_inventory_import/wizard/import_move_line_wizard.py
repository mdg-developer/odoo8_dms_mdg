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
#header_fields = ['default_code', 'product_name', 'public_price', 'uom', 'balance_qty', 'cost_price']
header_fields = ['product',  'uom', 'real quantity', 'serial number','theoretical quantity','location','pack','serial']

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
        stock_move_line_obj = self.pool.get('stock.inventory.line')
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
                    default_code_i =   uom_i = real_qty_i = theoretical_qty_i = serial_number_i =  None
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
                        elif header_field == 'product':
                            default_code_i = i
                        
                        elif header_field == 'uom':
                            uom_i = i
                        elif header_field == 'real quantity':
                            real_qty_i = i
                        elif header_field == 'serial number':
                            serial_number_i = i
                        elif header_field == 'theoretical quantity':
                            theoretical_qty_i = i
                    for f in [(default_code_i, 'product'), (theoretical_qty_i, 'theoretical quantity'), (uom_i, 'uom'), (real_qty_i, 'real quantity')]:
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
                   
                        import_vals['balance_qty'] = ln[real_qty_i]
                    if theoretical_qty_i > -1: 
                        import_vals['theoretical_qty'] = ln[theoretical_qty_i]
                    
                    if serial_number_i > -1: 
                        import_vals['serial_number'] = ln[serial_number_i]    
                    amls.append(import_vals)
                   
        if err_log:
            self.write(cr, uid, ids[0], {'note': err_log})
            self.write(cr, uid, ids[0], {'state': 'failed'})
        else:
            for aml in amls:
                default_code = uom_ids = uom_id = product_id = product_template_id = uom_name = theoretical_qty = product_qty = serial_number =  None
                value = []
                try:                                                   
                    if aml['default_code']:                        
                        default_code = aml['default_code']    
                                      
                    if aml['uom']:
                        uom_name = str(aml['uom']).strip()
                    else:
                        uom_name = 'Unit(s)'  # default uom
                    if aml['theoretical_qty']:
                        theoretical_qty = aml['theoretical_qty']
                        
                    if aml['balance_qty']:
                        product_qty = aml['balance_qty']
                        
                    if aml['serial_number']:
                        serial_number = str(aml['serial_number']).strip() #aml['serial_number']
                        
                    
                        
                    if uom_name:
                        uom_id = uom_obj.search(cr, uid, [('name', '=', uom_name)])
                        if not uom_id:
                            raise osv.except_osv(_('Error!'), _("UOM is not exist!"))
                            uom_ids = 'not contain'
                        else:
                            uom_ids = uom_id[0]
                            # print uom_ids                    
                    if default_code:
                        product_code = None
                        #first = default_code.index("[") + 1
                        #second = default_code.index("]")
                        #product_code = default_code[first:second]
                        cr.execute("""select id from product_product where lower(default_code) like %s """, (default_code.lower(),))
                        data = cr.fetchall()
                        if data:
                            product_id = data[0][0]
                        else:
                            product_id = None
                        serial = None    
                        if product_id:
                            cr.execute('select product_tmpl_id from product_product where id = %s', (product_id,))
                            product_template_id = cr.fetchone()
                            if move_id:
                                #cr.execute('select id from stock_inventory_line where inventory_id = %s and product_id = %s', (move_id, product_id,))
                                if serial_number:
                                    cr.execute("select id from stock_production_lot where name=%s and product_id = %s",(str(serial_number),product_id,))
                                    serial = cr.fetchone()
                                    cr.execute('select id from stock_inventory_line where inventory_id = %s and product_id = %s and prod_lot_id=%s', (move_id, product_id,serial,))
                                else:
                                    cr.execute('select id from stock_inventory_line where inventory_id = %s and product_id = %s and prod_lot_id is null', (move_id, product_id,))
                                        
                                exist = cr.fetchone()
                                # print 'exist ',exist
                                if not exist:
                                    value = {'inventory_id':move_id, 'product_uom_id':uom_ids, 'product_id':product_id, 'location_id':location_id, 'theoretical_qty': theoretical_qty , 'product_qty':product_qty}
#                                     stock_move_line_obj.create(cr, uid, value, context=context)
                                    cr.execute('insert into stock_inventory_line(inventory_id,product_uom_id,product_id,location_id,theoretical_qty,product_qty) \
                                                values(%s,%s,%s,%s,%s,%s)', (move_id,uom_ids,product_id,location_id,theoretical_qty,product_qty,))
                                else:
                                    value = {'theoretical_qty': theoretical_qty , 'product_qty':product_qty}
                                    stock_move_line_obj.write(cr, uid, exist, value)
                                res_id = 'product.template,'
                                res_id += str(product_template_id[0])
 
                except Exception, e:                    
                    continue        
                    
                
            self.write(cr, uid, ids[0], {'state': 'completed'})
  