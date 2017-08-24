'''
Created on Auguest 31, 2016

@author: Administrator
'''
import time

import os
from datetime import datetime
from datetime import timedelta  
from dateutil.relativedelta import relativedelta
from dateutil import parser
import time
from openerp.osv import fields , osv
from openerp.tools.translate import _
import datetime
import math
from datetime import datetime, timedelta

class good_receive_note(osv.osv):
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = "good.receive.note"
    _description = "Good receive Note"
    _order = "id desc"    
    _track = {
        'state': {
            'good_receive_note.good_receive_note_receive': lambda self, cr, uid, obj, ctx = None: obj.state in ['receive'],
            'good_receive_note.good_receive_note_check': lambda self, cr, uid, obj, ctx = None: obj.state in ['check']
        },
    }  
     
    def _get_default_branch(self, cr, uid, context=None):
        branch_id = self.pool.get('res.users')._get_branch(cr, uid, context=context)
        if not branch_id:
            raise osv.except_osv(_('Error!'), _('There is no default branch for the current user!'))
        return branch_id
        
      
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id   
    
    _columns = {
        'name': fields.char('GRN-Ref:No', readonly=True),
        'invoice_ref_no' : fields.char('Invoice Ref:No'),
        'rfr_ref_no' : fields.char('RFR- Ref:No'),
        'purchase_id' : fields.many2one('purchase.order', 'PO- Ref:No' , required=True),
        'bl_ref_no' : fields.char('B/L- Ref:No'),
       'branch_id':fields.many2one('res.branch', 'Branch'),
       'receiver_by':fields.many2one('res.users', "Received By"),
        'checked_by':fields.many2one('res.users', "Checked By"),
         'start_date':fields.date('Start Unloading Date'),
         'end_date':fields.date('End Unloading Date'),
        'no_of_container':fields.char('No. of Containers'),
        'state': fields.selection([
            ('draft', 'Pending'),
            ('receive', 'Received'),
            ('check', 'Checked'),
            ('cancel', 'Cancel'),
            ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
                 'p_line':fields.one2many('good.receive.note.line', 'line_id', 'Product Lines',
                              copy=True),
                'company_id':fields.many2one('res.company', 'Company'),
                                'partner_id':fields.many2one('res.partner', string='Partner'),
             'is_check':fields.selection([ ('deliver', 'Qty as per Doc'), ('receive', 'Total Recv Qty')], 'Check  Avaliable Space', required=True),
             'no_of_pallet':fields.integer('No. of Pallet Required'),
             'no_of_avspace':fields.integer('No. of Space Avaliable this principle'),
            'total_space':fields.integer('Total Avaliable Space'),
            'picking_id':fields.many2one('stock.picking', 'Picking'),
}
    _defaults = {
        'state' : 'draft',
         'company_id': _get_default_company,
         'branch_id': _get_default_branch,
         'is_check':'deliver',
    }     
    
    def on_change_purchase_id(self, cr, uid, ids, purchase_id, context=None):
        purchase_order_obj = self.pool.get('purchase.order')        
        picking_obj = self.pool.get('stock.picking')        
        move_obj = self.pool.get('stock.move')        
        values = {}
        data_line = []
        if purchase_id:        
            order_data = purchase_order_obj.browse(cr, uid, purchase_id, context=context)
            po_name = order_data.name
            order_ids = picking_obj.search(cr, uid, [('origin', '=', po_name), ('state', '!=', 'done')], context=context) 
            move_ids = move_obj.search(cr, uid, [('picking_id', 'in', order_ids), ('state', '!=', 'done')], context=context) 
            for line in move_ids:          
                line_data = move_obj.browse(cr, uid, line, context=context)
                product_id = line_data.product_id.id
                description = line_data.product_id.name_template
                quantity = line_data.product_uom_qty
                sequence = line_data.product_id.product_tmpl_id.sequence
                product_uom = line_data.product_uom.id
                
                data_line.append({
                                      'sequence':sequence,
                                        'product_id':product_id,
                                         'description': description,
                                        'deliver_quantity':quantity,
                                        'product_uom':product_uom,
                                          })                
            values = {
                'p_line': data_line,
            }
        return {'value': values}    
        
    def create(self, cursor, user, vals, context=None):
        id_code = self.pool.get('ir.sequence').get(cursor, user,
                                                'receive.code') or '/'
        vals['name'] = id_code
        return super(good_receive_note, self).create(cursor, user, vals, context=context)
    
    def receive(self, cr, uid, ids, context=None):
        picking_obj = self.pool.get('stock.picking')
        transfer_obj = self.pool.get('stock.transfer_details')
        transfer_items_obj = self.pool.get('stock.transfer_details_items')
        product_obj = self.pool.get('product.product')
        pallet_transfer_obj = self.pool.get('pallet.transfer')
        transfer_line_obj = self.pool.get('pallet.transfer.line')
        move_obj = self.pool.get('stock.move')        
        receive_data = self.browse(cr, uid, ids, context=context)
        po_name = receive_data.purchase_id.name
        pickList = picking_obj.search(cr, uid, [('origin', '=', po_name), ('state', '!=', 'done')], context=context) 
        wizResult = picking_obj.do_enter_transfer_details(cr, uid, pickList, context=context)
        detailObj = transfer_obj.browse(cr, uid, wizResult['res_id'], context=context)            
        if detailObj:
            for item in detailObj.item_ids:
                item_data = transfer_items_obj.browse(cr, uid, item.id, context=context)  
                product_id = item_data.product_id.id
                cr.execute('select product_uom,receive_quantity,batch_no from good_receive_note_line where product_id=%s and line_id=%s', (product_id, ids[0],))
                note_line_data = cr.fetchone()
                if note_line_data:
                    product_uom = note_line_data[0]
                    receive_quantity = note_line_data[1]
                    batch_no = note_line_data[2]
                product = product_obj.browse(cr, uid, product_id, context=context)
                if product_uom == product.product_tmpl_id.big_uom_id.id:                                                                          
                    cr.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (product.product_tmpl_id.big_uom_id.id,))
                    bigger_qty = cr.fetchone()[0]
                    bigger_qty = int(bigger_qty)
                    receive_quantity = bigger_qty * receive_quantity           
                transfer_items_obj.write(cr, uid, item_data.id, {'quantity':receive_quantity, 'lot_id':batch_no}, context=context)    
            detailObj.allocate_pallet()
            detailObj.do_detailed_transfer()    
            pallet_id = pallet_transfer_obj.create(cr, uid, {
                                                  'good_receive_id': ids[0],
                                                  'receive_date': datetime.now(),
                                                  'transfer_date':datetime.now(),
                                                  'branch_id':receive_data.branch_id.id, })
            cr.execute("select location_dest_id,result_package_id,product_qty,lot_id,product_id from stock_pack_operation where picking_id =%s", (pickList[0],))
            pallete_data = cr.fetchall()
            if pallete_data:
                for pallete in pallete_data:
                    if pallete[3] is not None:
                        cr.execute("select life_date from stock_production_lot where id =%s", (pallete[3],))
                        expiry_date = cr.fetchone()[0]
                    else:
                        expiry_date=None
                    transfer_line_obj.create(cr, uid, {'line_id': pallet_id,
                                                  'pallet_id': pallete[1],
                                                  'quantity':pallete[2],
                                                  'lot_id':pallete[3],
                                                  'expiry_date':expiry_date ,
                                                  'product_id':pallete[4],
                                                  'src_location_id': pallete[0],
                                                  'dest_location_id':None,
                                                  }, context=context)                           
        return self.write(cr, uid, ids, { 'receiver_by':uid, 'state':'receive', 'picking_id':pickList[0]})
    
    def cancel(self, cr, uid, ids, context=None):
        
        return self.write(cr, uid, ids, {'state':'cancel' })
    
    def check(self, cr, uid, ids, context=None):


        return self.write(cr, uid, ids, {'checked_by':uid, 'state':'check' })    
    
    
    
    def check_space(self, cr, uid, ids, context=None):
        
        if ids:
            receive_line_obj = self.pool.get('good.receive.note.line')
            product_obj = self.pool.get('product.product')
            mapping_obj = self.pool.get('pallet.mapping')
            quant_obj = self.pool.get('stock.quant')
            location_obj = self.pool.get('stock.location')
            require_pallet = 0
            avaliable_space = 0
            total_space = 0
            line_require_pallet = 0
            receive_data = self.browse(cr, uid, ids, context=context)
            is_check = receive_data.is_check
            drop_location_id = receive_data.purchase_id.picking_type_id.default_location_dest_id.id
            receive_line_ids = receive_line_obj.search(cr, uid, [('line_id', '=', ids[0])], context=context) 
            for line_id in receive_line_ids:
                line = receive_line_obj.browse(cr, uid, line_id, context=context)
                product_id = line.product_id.id
                product_uom = line.product_uom.id
                deliver_qty = line.deliver_quantity
                receive_qty = line.receive_quantity
                if is_check == 'deliver':
                    total_qty = deliver_qty
                else:
                    total_qty = receive_qty
                product = product_obj.browse(cr, uid, product_id, context=context)
                principle_id = product.product_tmpl_id.main_group.id
                if product_uom == product.product_tmpl_id.big_uom_id.id:                                                                          
                    cr.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (product.product_tmpl_id.big_uom_id.id,))
                    bigger_qty = cr.fetchone()[0]
                    bigger_qty = int(bigger_qty)
                    total_qty = bigger_qty * total_qty
                mapping_ids = mapping_obj.search(cr, uid, [('product_id', '=', product_id)], context=context) 
                mapping_data = mapping_obj.browse(cr, uid, mapping_ids, context=context)
                smaller_qty = mapping_data.smaller_qty
                if total_qty <= smaller_qty:
                    require_pallet = require_pallet + 1;
                    line_require_pallet=1;
                else:
                    require_pallet = require_pallet + (total_qty / smaller_qty)
                    line_require_pallet=round((total_qty / smaller_qty))
                    lastest_qty = (total_qty % smaller_qty)          
                    if lastest_qty > 0:
                        require_pallet = require_pallet + 1;
                        line_require_pallet =line_require_pallet +1;
                receive_line_obj.write(cr, uid, line_id, {'no_of_pallet_required': line_require_pallet})           
            cr.execute("""select sl.id from product_product pp ,product_template pt ,stock_location sl 
            where pp.product_tmpl_id =pt.id 
            and pt.main_group=sl.maingroup_id
            and sl.location_id=%s
            and pt.main_group = %s
            group by  sl.id,pt.main_group""", (drop_location_id, principle_id,))
            location_ids = cr.fetchall()
            for location in location_ids:
                location_id = location[0]
                quant_id = quant_obj.search(cr, uid, [('location_id', '=', location_id), ('qty', '>', 0)], context=context) 
                if len(quant_id) == 0:
                    avaliable_space = avaliable_space + 1;       
            total_location_ids = location_obj.search(cr, uid, [('location_id', '=', drop_location_id)], context=context) 
            for location in total_location_ids:
                quant_id = quant_obj.search(cr, uid, [('location_id', '=', location), ('qty', '>', 0)], context=context) 
                if len(quant_id) == 0:
                    total_space = total_space + 1;                   
        return self.write(cr, uid, ids, {'no_of_pallet': require_pallet, 'no_of_avspace':avaliable_space, 'total_space':total_space})  
            
 
                            
class good_receive_line(osv.osv):  # #prod_pricelist_update_line
    _name = 'good.receive.note.line'
    _description = 'Receive Note Line'


    def on_change_product_id(self, cr, uid, ids, product_id, context=None):
        values = {}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            values = {
                'sequence': product.product_tmpl_id.sequence,
                'description':product.name_template,
                'product_uom':product.product_tmpl_id.uom_id,
            }
        return {'value': values}
        
    def on_change_expired_date(self, cr, uid, ids, batch_no, context=None):
        values = {}
        if batch_no:
            lot_obj = self.pool.get('stock.production.lot').browse(cr, uid, batch_no, context=context)
            values = {
                'expiry_date': lot_obj.life_date,
            }
        return {'value': values}    
    
    def on_change_different_qty(self, cr, uid, ids, deliver_quantity, receive_quantity, context=None):
        values = {}
        different_quantity = 0
        if deliver_quantity >= 0:
            different_quantity = deliver_quantity - receive_quantity
            
            values = {
                'different_quantity':different_quantity,
            }
        return {'value': values}            
    
    _columns = {                
        'line_id':fields.many2one('good.receive.note', 'Line', ondelete='cascade', select=True),
        'state': fields.related('line_id', 'state', string='Status', readonly=True, type='selection', selection=[
            ('draft', 'Pending'),
            ('receive', 'Received'),
            ('check', 'Checked'),
            ('cancel', 'Cancel'),
            ]),
        'description':fields.char('Item Specification'),
        'product_id': fields.many2one('product.product', 'Item Description', required=True),
        'deliver_quantity' : fields.float(string='Qty as per Doc', digits=(16, 0)),
        'receive_quantity' : fields.float(string='Total Recv Qty', digits=(16, 0)),
        'different_quantity' : fields.float(string='Qty in Diff', digits=(16, 0)),
        'product_uom': fields.many2one('product.uom', 'Smaller UoM'),
        'batch_no':fields.many2one('stock.production.lot', 'Batch No'),
         'expiry_date':fields.date('Expiry'),
         'remark':fields.char('Remark'),
        'sequence':fields.integer('Sequence'),
        'product_uom':fields.many2one('product.uom', 'UOM'),
        'no_of_pallet_required':fields.integer('No. of pallet required'),
    }
        
   
    
