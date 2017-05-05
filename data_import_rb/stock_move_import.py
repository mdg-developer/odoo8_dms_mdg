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
header_fields =  ['From Location','To Location','Transfer Date','Product','UOM','Quantity']

class stock_move_import(osv.osv):
    _name = 'stock.import'
    _description = 'Import inventory adjust product lines'
    _columns = {
                'name':fields.char('Description'),
                'import_date':fields.date('Import Date',readonly=True),
                'file': fields.binary('File', required=True),
                'filename': fields.char('Filename', size=128),
              #  'from_location_id':fields.many2one('stock.location','Source Location'),
              #  'to_location_id':fields.many2one('stock.location','Destination Location'),
                'inventory_date':fields.date('Inventory Date', required=True),
                'date_expected':fields.date('Date Expected', required=True),
                'company_id':fields.many2one('res.company',"Company"),
                'note':fields.text('Log'),
                'state':fields.selection([
                    ('draft', 'Draft'),
                    ('pending','Pending'),
                  #  ('confirm', 'Confirm'),
                    ('transfered','Transferd'),
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
    
    _constraints = [(_check_file_ext,"Please import Excel file!",['import_fname'])]
    
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
            #replace the None the dictionary by False, because falsy values are tested later on
            for key, value in product_line.items():
                if not value:
                    product_line[key] = False
            #product_line['inventory_id'] = inventory.id
            product_line['theoretical_qty'] = product_line['product_qty']
            if product_line['product_id']:
                product = product_obj.browse(cr, uid, product_line['product_id'], context=context)
                product_line['product_uom_id'] = product.uom_id.id
            vals.append(product_line)
        return vals 
    def transfer(self, cr, uid, ids, context=None): 
        stock_move_obj= self.pool.get('stock.move')
        stock_line_obj  = self.pool.get('stock.import.line')
        data = self.browse(cr,uid,ids)[0]
        company_id =data.company_id.id
        line_ids = stock_line_obj.search(cr,uid,[('line_id','=',data.id)])
        if line_ids:
            for id in line_ids:
                data=stock_line_obj.browse(cr,uid,id,context=context)
                move_val={
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
                          'location_dest_id':data.location_dest_id.id,
                          'create_date':data.create_date,
                          'state':'done'}
                move_id =stock_move_obj.create(cr,uid,move_val,context=context)
                print 'this is stock_move id',move_id
                stock_move_obj.action_done(cr, uid, move_id, context=context)
        print 'done '
        self.write(cr, uid, ids[0], {'state': 'transfered'})
        return True
    
    def excel_import(self, cr, uid, ids, context=None):
        
        template_obj = self.pool.get('product.template')
        att_obj =self.pool.get('product.attribute')
        uom_obj = self.pool.get('product.uom')
        product_obj = self.pool.get('product.product')
        location_obj = self.pool.get('stock.location')
        stock_move_obj =self.pool.get('stock.move')
        stock_location_obj = self.pool.get('stock.location')
        stock_line_obj = self.pool.get('stock.import.line')
        data = self.browse(cr,uid,ids)[0]
        company_id = data.company_id.id
        product_list = from_location = to_location =date_expected= None

        #print 'move_id',move_id
        locations = location_obj.read(cr,uid,location_obj.search(cr,uid,[('active','=',True),('company_id','=',company_id)]),['name'])
        location=locations[1]
        data = self.browse(cr,uid,ids)[0]
        import_file = data.file
        import_filename = data.filename

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
                    product_i = product_uom_i = product_qty_i = to_location_id_i = from_location_id_i = transfer_date_i = None
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
                      
                        elif header_field == 'Product':
                            product_i = i
                        elif header_field == 'UOM':
                            product_uom_i = i
                        elif header_field == 'Quantity':
                            product_qty_i = i
                        elif header_field == 'From Location':
                            from_location_id_i = i
                        elif header_field == 'To Location':
                            to_location_id_i = i
                        elif header_field == 'Transfer Date':
                            transfer_date_i = i
                                                        
                    for f in [(transfer_date_i,'Transfer Date'),(from_location_id_i,'From Location'),(to_location_id_i,'To Location'),(product_i,'Product'),(product_uom_i,'UOM'),(product_qty_i,'Quantity')]:
                        if not isinstance(f[0],int):
                            err_log += '\n'+ _("Invalid Excel file, Header '%s' is missing !") % f[1]
                        
                #process data lines   
            else:
                if ln and ln[0] and ln[0][0] not in ['#','']:
                    
                    import_vals = {}
                    import_vals['Product'] =  ln[product_i]
                    import_vals['UOM'] = ln[product_uom_i]
                    import_vals['Quantity'] = ln[product_qty_i]
                    import_vals['From Location'] = ln[from_location_id_i]
                    import_vals['To Location'] = ln[to_location_id_i]
                    import_vals['Transfer Date'] = ln[transfer_date_i]
                    amls.append(import_vals)
                  
        if err_log:
            self.write(cr, uid, ids[0], {'note': err_log})
            #print 'this is err_log ',err_log
            self.write(cr, uid, ids[0], {'state': 'failed'})
        else:
            for aml in amls:
                product_id =uom_id = uom_ids = None
                product_name=uom_name = quantity = total_qty = to_location_id = transfer_date =  None
                
                from_location = str(aml['From Location'])
                to_location = str(aml['To Location'])
                transfer_date = float(aml['Transfer Date'])
                if transfer_date:
                    result = xlrd.xldate.xldate_as_tuple(transfer_date, 0)
                    a = str(result[1]) + '/' + str(result[2]) + '/' + str(result[0]) + ' ' + str(result[3]) + ':' + str(result[4]) + ':' + str(result[5])
                    date_expected = datetime.strptime(a, '%m/%d/%Y %H:%M:%S')
                else:
                    date_expected = datetime.now()
                if to_location:
                    print 'to location',to_location
                    if to_location.find('/') != -1:
                        parent_child =to_location.split('/')
                        if parent_child:
                            parent_wh = parent_child[0]
                            child_wh = parent_child[1]
                            parent_id = stock_location_obj.search(cr,uid,[('name','=',parent_wh)])
                            if parent_id:
                                child_id = stock_location_obj.search(cr,uid,['&',('name','=',child_wh),('location_id','=',parent_id[0])])
                                if child_id:
                                    to_location_id=child_id[0]
                    else:
                        to_id = stock_location_obj.search(cr,uid,[('name','=',to_location)])
                        if to_id:
                            to_location_id=to_id[0]
                            
                                    
                if from_location:
                    print 'from location',from_location
                    if from_location.find('/') != -1:
                        print 'found /'
                        parent_child =from_location.split('/')
                        print 'parent and child',parent_child
                        if parent_child:
                            parent_wh = parent_child[0]
                            child_wh = parent_child[1]
                            parent_id = stock_location_obj.search(cr,uid,[('name','=',parent_wh)])
                            print 'parent id',parent_id
                            if parent_id:
                                print 'child value',child_wh
                                child_id = stock_location_obj.search(cr,uid,['&',('name','=',child_wh),('location_id','=',parent_id[0])])
                                print 'child id ',child_id
                                if child_id:
                                    print 'found /'
                                    from_location_id = child_id[0]
                                    product_list = self.get_product_from_inventory(cr,uid,from_location_id,context=context)
                    else:
                        print 'No Warehouse'
                        from_id = stock_location_obj.search(cr,uid,[('name','=',from_location)])
                        if from_id:
                            print ' Not found /'
                            from_location_id=from_id[0]
                            product_list = None
                if product_list:
                    move_val={}
                    product_name=str(aml['Product'])
                    uom_name = str(aml['UOM'])
                    quantity = float(aml['Quantity'])
                    print 'name',product_name,',uom name',uom_name
                    if quantity:
                        move_val['product_uom_qty']=quantity
                    if from_location:
                        move_val['location_id']=from_location_id
                    if to_location:
                        move_val['location_dest_id']=to_location_id
                    if date_expected:
                        move_val['date_expected'] =date_expected
                    #this condition for product and uom are contain or not in excel
                    if product_name and uom_name:
                        #print 'they are same'
                        product_id=product_obj.search(cr,uid,[('name_template','=',product_name)])
                        uom_id = uom_obj.search(cr,uid,[('name','=',uom_name)])
                        #print 'product id',product_id,'uom -id,',uom_id
                        #after existing in excel need to check their uom is same or not
                        #if same ,can transfer
                        #if not same,can't transfer
                        if product_id:
                            product =product_obj.browse(cr, uid, product_id[0], context=context)
                            uom_ids = product.uom_id.id
                            #I check the actual product uom id with uom in excel are same or not
                            #if they are same together next conditin will go to transfer
                        if uom_id and uom_ids:
                            #we need to check these products are in source location if not in source location ,we can't transfer
                            if uom_id[0]==uom_ids:
                                                
    
                                for product_item in product_list:
                                    if product_id[0]==product_item['product_id'] and uom_ids==product_item['product_uom_id']:
                                        move_val['product_id']=product_item['product_id']
                                        move_val['product_uom']=product_item['product_uom_id']
                                        move_val['theoretical_qty'] = product_item['theoretical_qty']
                                        move_val['origin']='Import'
                                        move_val['line_id'] = data.id
                                        line_id =stock_line_obj.search(cr,uid,['&',('line_id','=',data.id),('product_id','=',move_val['product_id'])])
                                        #print 'line -id',id
                                        if not line_id:
                                            stock_line_obj.create(cr,uid,move_val,context=context)
                                        else:
                                            #line id is exist
                                            #print 'this is prod id ',pro_id
                                            pro_id=stock_line_obj.browse(cr,uid,line_id[0],context=context)
                                            #print 'product id is same',pro_id.product_id.id ,move_val['product_id']
                                            total_qty=pro_id.product_uom_qty+move_val['product_uom_qty']
                                            stock_line_obj.write(cr,uid,pro_id.id,{'product_uom_qty':total_qty},context=context)
                                        
     
                            else:
                                print 'uom id are not same'
                #print 'this is aml',aml
                self.write(cr, uid, ids[0], {'state': 'pending'})  
        return True
stock_move_import()                     
class stock_line(osv.osv):   
    _name = 'stock.import.line'
    _description ='Stock Lines Import'
    _columns = {     
                'product_id':fields.many2one('product.product','Product'),
                'product_uom':fields.many2one('product.uom','Product Unit of Measure'),
                'theoretical_qty':fields.float('Stock Quantity'),
                'product_uom_qty':fields.float('Transfer Quantity'),
                'location_id':fields.many2one('stock.location',"Source Location"),
                'location_dest_id':fields.many2one('stock.location',"Destination Location"),
                  'line_id': fields.many2one('stock.import', 'Order Reference', required=True, ondelete='cascade', select=True, readonly=True, states={'draft':[('readonly',False)]}),
                  'origin':fields.char('Origin'),
                  'date_expected':fields.date('To Date')
                }
      
stock_line()                    




