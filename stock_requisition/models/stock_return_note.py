'stock.location','''
Created on Sept 14, 2016

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

class stock_return_note(osv.osv):
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = "stock.return.note"
    _description = "Stock Return Note(SRN)"
    _order = "id desc"    
#     _track = {
#         'state': {
#             'stock_taking_loading_instruction.mt_note_confirm': lambda self, cr, uid, obj, ctx = None: obj.state in ['confirm'],
#             'stock_taking_loading_instruction.mt_note_approve': lambda self, cr, uid, obj, ctx = None: obj.state in ['approve']
#         },
#     }    
        
    
    _columns = {
                'request_gin_id':fields.char('(GIN) Ref:No.', readonly=True),
                'return_from':fields.char('Return From'),
                'return_date':fields.date('Date of Return'),
                'name': fields.char('(SRN) Ref:No.', readonly=True),                
                'sale_order_inv_id':fields.char('Sale Order/Inv Ref:No.', readonly=True),
                'vehicle_id':fields.many2one('fleet.vehicle', 'Vehicle No.'), 
        
#         'state': fields.selection([
#             ('draft', 'Pending'),
#               ('confirm', 'Sale Manager Approved'),
#             ('approve', 'WH Manager Approved'),
#             ('cancel', 'Cancel')
#             ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
#               \nThe exception status is automatically set when a cancel operation occurs \
#               in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
#                but waiting for the scheduler to run on the order date.", select=True),
      'p_line':fields.one2many('stock.return.note.line', 'line_id', 'Product Lines',
                              copy=True),
                
}
    _defaults = {
        'state' : 'draft',
         
    }     
    def create(self, cursor, user, vals, context=None):
        id_code = self.pool.get('ir.sequence').get(cursor, user,
                                                'stock.return.note.code') or '/'
        vals['name'] = id_code
        return super(stock_return_note, self).create(cursor, user, vals, context=context)
    
    def cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel', })
    
    def confirm(self, cr, uid, ids, context=None):
        product_line_obj = self.pool.get('stock.return.note.line')
        note_obj = self.pool.get('stock.return.note')
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')

        note_value = req_lines = {}
        if ids:
            note_value = note_obj.browse(cr, uid, ids[0], context=context)
            issue_date = note_value.issue_date
            location_id = note_value.to_location_id.id
            from_location_id = note_value.from_location_id.id
            origin = note_value.name
            partner_id = 106
            cr.execute('select id from stock_picking_type where default_location_dest_id=%s and name like %s', (location_id, '%Internal Transfer%',))
            price_rec = cr.fetchone()
            if price_rec: 
                picking_type_id = price_rec[0] 
            else:
                raise osv.except_osv(_('Warning'),
                                     _('Picking Type has not for this transition'))
            picking_id = picking_obj.create(cr, uid, {
                                          'date': issue_date,
                                          'origin':origin,
                                          'picking_type_id':picking_type_id}, context=context)
            note_line_id = product_line_obj.search(cr, uid, [('line_id', '=', ids[0])], context=context)
            if note_line_id and picking_id:
                
                for id in note_line_id:
                    note_line_value = product_line_obj.browse(cr, uid, id, context=context)
                    product_id = note_line_value.product_id.id
                    name = note_line_value.product_id.name_template
                    product_uom = note_line_value.product_uom.id
                    origin = origin
                    quantity = note_line_value.issue_quantity
                    move_obj.create(cr, uid, {'picking_id': picking_id,
                                              'picking_type_id':picking_type_id,
                                          'product_id': product_id,
                                          'product_uom_qty': quantity,
                                          'product_uos_qty': quantity,
                                          'product_uom':product_uom,
                                          'location_id':location_id,
                                          'location_dest_id':from_location_id,
                                          'name':name,
                                           'origin':origin,
                                          'state':'confirmed'}, context=context)        
        return self.write(cr, uid, ids, {'state':'confirm'})    
    
    def approve(self, cr, uid, ids, context=None):
         move_obj = self.pool.get('stock.move')
         if ids:
            note_value = self.browse(cr, uid, ids[0], context=context)
            note_ref = note_value.name
            move_id = move_obj.search(cr, uid, [('origin', '=', note_ref)], context=context)

            for stock_id in move_id:
                print 'idddddddddd', stock_id
                move_obj.action_done(cr, uid, stock_id, context=context)
         return self.write(cr, uid, ids, {'state':'approve'})    

            
class stock_return_note_line(osv.osv):  # #prod_pricelist_update_line
    _name = 'stock.return.note.line'
    _description = 'Note Line'

    def on_change_product_id(self, cr, uid, ids, product_id, context=None):
        values = {}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            values = {
                'product_uom': product.product_tmpl_id.uom_id and product.product_tmpl_id.uom_id.id or False,
                'uom_ratio': product.product_tmpl_id.uom_ratio,
            }
        return {'value': values}
        
    _columns = {                
        'line_id':fields.many2one('stock.return.note', 'Line', ondelete='cascade', select=True),        
        'product_id': fields.many2one('product.product', 'Product', required=True),   
        'product_uom': fields.many2one('product.uom', 'UOM', required=True), 
        'issue_quantity' : fields.float(string='ISSUED QTY', digits=(16, 0)),
        'return_quantity' : fields.float(string='RETURNED QTY', digits=(16, 0)),
        'sales_quantity' : fields.float(string='SALES QTY', digits=(16, 0)),
        'foc_quantity' : fields.float(string='FOC QTY', digits=(16, 0)),         
        'uom_ratio':fields.char('PACKING UNIT'),
         'actual_rec_quantity' : fields.float(string='QTY(ACTUAL REC:)', digits=(16, 0)),              
        'batch_no':fields.many2one('stock.production.lot','Batch No'),
        'expiry_date':fields.date('Expiry'),
        'remark':fields.char('Remark'),
            }
        
   
    
