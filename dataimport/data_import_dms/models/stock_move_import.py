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
import xlrd
_logger = logging.getLogger(__name__)
header_fields = ['from location', 'to location', 'transfer date', 'product', 'uom', 'quantity', 'tg_no']

class stock_move_import(osv.osv):
    _name = 'stock.import'
    _description = 'Import inventory adjust product lines'
    _columns = {
                'name':fields.char('Description'),
                'import_date':fields.date('Import Date', readonly=True),
                'file': fields.binary('File', required=True),
                'filename': fields.char('Filename', size=10),
                'inventory_date':fields.date('Inventory Date', required=True),
                'date_expected':fields.date('Date Expected', required=True),
                'company_id':fields.many2one('res.company', "Company", required=True),
                'picking_type':fields.selection([
                    ('receipts', 'Receipts'),
                    ('internal_transfer', 'Internal Transfers'),
                    ('delivery_order', 'Delivery Order')
                ], 'Picking Type', required=True),
                'note':fields.text('Note'),
                'state':fields.selection([
                    ('draft', 'Draft'),
                    ('pending', 'Pending'),
                  #  ('confirm', 'Confirm'),
                    ('transfered', 'Transferd'),
                    ('error', 'Error'),
                ], 'States'),
               'stock_line_ids': fields.one2many('stock.import.line', 'line_id', 'Order Lines', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=True),
    }
    _defaults = {
        'import_date':datetime.now(),
        'inventory_date':datetime.now(),
        'date_expected':datetime.now(),
        'state':'draft'
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
    def transfer(self, cr, uid, ids, context=None): 
        stock_move_obj = self.pool.get('stock.move')
        stock_line_obj = self.pool.get('stock.import.line')
        stock_picking_obj = self.pool.get('stock.picking')
        picking_type = warehouse_id = dest_loc_id = picking_type_id = picking_id = None
        data = self.browse(cr, uid, ids)[0]
        company_id = data.company_id.id
        if data.picking_type:
            picking_type = data.picking_type
        line_ids = stock_line_obj.search(cr, uid, [('line_id', '=', data.id)])
        move_val={}
        if line_ids:
            for id in line_ids:
                data = stock_line_obj.browse(cr, uid, id, context=context)
                dest_loc_id = data.location_dest_id.id
                if picking_type:
                    cr.execute("""select id from stock_warehouse where lot_stock_id=%s """, (dest_loc_id,))
                    data1 = cr.fetchall()
                    if data1:
                        warehouse_id = data1[0]
                if warehouse_id and picking_type:
                    if picking_type == 'receipts':
                        cr.execute("""select id from stock_picking_type where warehouse_id=%s and lower(name) like 'receipts' """, (warehouse_id,))
                        data1 = cr.fetchall()
                        if data1:
                            picking_type_id = data1[0]
                    if picking_type == 'internal_transfer':
                        cr.execute("""select id from stock_picking_type where warehouse_id=%s and lower(name) like 'internal transfers' """, (warehouse_id,))
                        data1 = cr.fetchall()
                        if data1:
                            picking_type_id = data1[0]
                        
                    if picking_type == 'delivery_order':
                        cr.execute("""select id from stock_picking_type where warehouse_id=%s and lower(name) like 'delivery orders' """, (warehouse_id,))
                        data1 = cr.fetchall()
                        if data1:
                            picking_type_id = data1[0]
                if picking_type_id:
                    res = {
                                'move_type':'direct',
                                'invoice_state':'none',
                                'picking_type_id':picking_type_id,
                                'priority':'1'}
                    picking_id = stock_picking_obj.create(cr, uid, res, context)    
                move_val = {
                          'name':'Import',
                          'product_id':data.product_id.id,
                          'product_uom_qty':data.product_uom_qty,
                          'product_uom':data.product_uom.id,
                          'selection':'none',
                          'priority':'1',
                          'company_id':company_id,
                          'date_expected':data.date_expected,
                          'date':data.date_expected,
                          'origin':data.origin,
                          'location_id':data.location_id.id,
                          'location_dest_id':dest_loc_id,
                          'create_date':data.create_date,
                          'picking_type_id':picking_type_id,
                          'picking_id':picking_id,
                          'state':'done'}
                move_id = stock_move_obj.create(cr, uid, move_val, context=context)
                stock_move_obj.action_done(cr, uid, move_id, context=context)
        self.write(cr, uid, ids[0], {'state': 'transfered'})
        return True
    
    def excel_import(self, cr, uid, ids, context=None):
        template_obj = self.pool.get('product.template')
        att_obj = self.pool.get('product.attribute')
        uom_obj = self.pool.get('product.uom')
        product_obj = self.pool.get('product.product')
        location_obj = self.pool.get('stock.location')
        stock_move_obj = self.pool.get('stock.move')
        stock_location_obj = self.pool.get('stock.location')
        stock_line_obj = self.pool.get('stock.import.line')
        data = self.browse(cr, uid, ids)[0]
        company_id = data.company_id.id
        product_list = from_location = to_location = date_expected = None

        data = self.browse(cr, uid, ids)[0]
        import_file = data.file
        import_filename = data.filename

        err_log = ''
        header_line = False

        lines = base64.decodestring(import_file)
        wb = open_workbook(file_contents=lines)
        excel_rows = []
        
        for s in wb.sheets():
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
                    product_i = product_uom_i = product_qty_i = to_location_id_i = from_location_id_i = transfer_date_i = tg_no_i = None
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
                            err_log += '\n' + _("Invalid Excel File, Header Field '%s' is not supported !") % ln[i]
                        # required header fields : account, debit, credit
                      
                        elif header_field == 'product':
                            product_i = i
                        elif header_field == 'uom':
                            product_uom_i = i
                        elif header_field == 'quantity':
                            product_qty_i = i
                        elif header_field == 'from location':
                            from_location_id_i = i
                        elif header_field == 'to location':
                            to_location_id_i = i
                        elif header_field == 'transfer date':
                            transfer_date_i = i
                        elif header_field == 'tg_no':
                            tg_no_i = i
                                                        
                    for f in [(tg_no_i, 'tg_no'), (transfer_date_i, 'transfer date'), (from_location_id_i, 'from location'), (to_location_id_i, 'to location'), (product_i, 'product'), (product_uom_i, 'uom'), (product_qty_i, 'quantity')]:
                        if not isinstance(f[0], int):
                            err_log += '\n' + _("Invalid Excel file, Header '%s' is missing !") % f[1]
                        
                # process data lines   
            else:
                # add the without value for without header fields columns
                for i in range(0, val):
                    ln.append('')
                if ln and ln[0] and ln[0][0] not in ['#', '']:
                    
                    import_vals = {}
                    import_vals['product'] = ln[product_i]
                    import_vals['uom'] = ln[product_uom_i]
                    import_vals['quantity'] = ln[product_qty_i]
                    import_vals['from location'] = ln[from_location_id_i]
                    import_vals['to location'] = ln[to_location_id_i]
                    import_vals['transfer date'] = ln[transfer_date_i]
                    import_vals['tg_no'] = ln[tg_no_i]
                    amls.append(import_vals)
                  
        if err_log:
            self.write(cr, uid, ids[0], {'note': err_log})
            # print 'this is err_log ',err_log
            self.write(cr, uid, ids[0], {'state': 'error'})
        else:
            for aml in amls:
                product_id = uom_id = uom_ids = None
                product_list = product_name = uom_name = total_qty = from_location_id = to_location_id = transfer_date = tg_no = None
                quantity = 0.0
                p_id = c_id = None
                
                if aml['from location']:
                    from_location = str(aml['from location'])
                if aml['to location']:
                    to_location = str(aml['to location'])
                if aml['transfer date']:
                    transfer_date = float(aml['transfer date'])
                if aml['product']:
                    product_name = str(aml['product'])
                if aml['uom']:
                    uom_name = str(aml['uom'])
                if aml['tg_no']:
                    tg_no = str(aml['tg_no'])
                    tg_no = tg_no.strip()
                if transfer_date:
                    result = xlrd.xldate.xldate_as_tuple(transfer_date, 0)
                    a = str(result[1]) + '/' + str(result[2]) + '/' + str(result[0]) + ' ' + str(result[3]) + ':' + str(result[4]) + ':' + str(result[5])
                    date_expected = datetime.strptime(a, '%m/%d/%Y %H:%M:%S')
                else:
                    date_expected = datetime.now()
                if to_location:
                    to_location = to_location.strip()
                    cr.execute("""select id from stock_location where lower(name) like %s """, (to_location.lower(),))
                    data3 = cr.fetchall()
                    if data3:
                        to_location_id = data3[0][0]
                if from_location:
                    from_location = from_location.strip()
                    cr.execute("""select id from stock_location where lower(name) like %s """, (from_location.lower(),))
                    data4 = cr.fetchall()
                    if data4:
                        from_location_id = data4[0][0]
                    if from_location_id:
                        product_list = self.get_product_from_inventory(cr, uid, from_location_id, context=context)
                if product_list:
                    move_val = {}
                    product_name = product_name.strip()
                    uom_name = uom_name.strip()
                if aml['quantity']:
                    quantity = float(aml['quantity'])
                    if quantity:
                        move_val['product_uom_qty'] = quantity
                    if from_location:
                        move_val['location_id'] = from_location_id
                    if to_location:
                        move_val['location_dest_id'] = to_location_id
                    if date_expected:
                        move_val['date_expected'] = date_expected
                    # this condition for product and uom are contain or not in excel
                if product_name and uom_name:
                    # print 'they are same'
                    cr.execute("""select id from product_product where lower(name_template) like %s """, (product_name.lower(),))
                    data1 = cr.fetchall()
                    if data1:
                        product_id = data1[0]
                        
                    cr.execute(""" select id from product_uom where lower(name) like %s """, (uom_name.lower(),))
                    data2 = cr.fetchall()
                    if data2:
                        uom_id = data2[0]
                    # print 'product id',product_id,'uom -id,',uom_id
                    # after existing in excel need to check their uom is same or not
                    # if same ,can transfer
                    # if not same,can't transfer
                if product_id:
                    product = product_obj.browse(cr, uid, product_id[0], context=context)
                    uom_ids = product.uom_id.id
                    # I check the actual product uom id with uom in excel are same or not
                    # if they are same together next conditin will go to transfer
                if uom_id and uom_ids:
                    # we need to check these products are in source location if not in source location ,we can't transfer
                    if uom_id[0] == uom_ids:
                        for product_item in product_list:
                            if product_id[0] == product_item['product_id'] and uom_ids == product_item['product_uom_id'] and from_location_id == product_item['location_id']:
                                move_val['product_id'] = product_item['product_id']
                                move_val['product_uom'] = product_item['product_uom_id']
                                move_val['theoretical_qty'] = product_item['theoretical_qty']
                                move_val['origin'] = tg_no
                                move_val['line_id'] = data.id
                                line_id = stock_line_obj.search(cr, uid, ['&', ('date_expected', '=', date_expected), ('line_id', '=', data.id), ('product_id', '=', move_val['product_id']), ('location_id', '=', from_location_id), ('location_dest_id', '=', to_location_id)])
                                # print 'line -id',id
                                if not line_id and quantity > 0:
                                    stock_line_obj.create(cr, uid, move_val, context=context)
                                    break
                                elif line_id and quantity > 0:
                                    # line id is exist
                                    # print 'this is prod id ',pro_id
                                    pro_id = stock_line_obj.browse(cr, uid, line_id[0], context=context)
                                    # print 'product id is same',pro_id.product_id.id ,move_val['product_id']
                                    total_qty = pro_id.product_uom_qty + move_val['product_uom_qty']
                                    stock_line_obj.write(cr, uid, pro_id.id, {'product_uom_qty':total_qty}, context=context)
                                    break
                                    
 
                        else:
                            print 'uom id are not same'
                # print 'this is aml',aml
                self.write(cr, uid, ids[0], {'state': 'pending'})  
        return True
stock_move_import()                     
class stock_line(osv.osv):   
    _name = 'stock.import.line'
    _description = 'Stock Lines Import'
    _columns = {     
                'product_id':fields.many2one('product.product', 'Product'),
                'product_uom':fields.many2one('product.uom', 'Product Unit of Measure'),
                'theoretical_qty':fields.float('Stock Quantity'),
                'product_uom_qty':fields.float('Transfer Quantity'),
                'location_id':fields.many2one('stock.location', "Source Location"),
                'location_dest_id':fields.many2one('stock.location', "Destination Location"),
                  'line_id': fields.many2one('stock.import', 'Order Reference', required=True, ondelete='cascade', select=True, readonly=True, states={'draft':[('readonly', False)]}),
                  'origin':fields.char('Origin'),
                  'date_expected':fields.date('To Date')
                }
      
stock_line()                    




