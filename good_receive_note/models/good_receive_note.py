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
         'start_date':fields.date('Start Unloading Date', required=True),
         'end_date':fields.date('Start Unloading Date', required=True),
        'no_of_container':fields.char('No of Containers'),
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

}
    _defaults = {
        'state' : 'draft',
         'company_id': _get_default_company,
         'branch_id': _get_default_branch,
    }     
    def on_change_purchase_id(self, cr, uid, ids, purchase_id, context=None):
        receive_obj = self.browse(cr, uid, ids, context=context)
        purchase_order_line_obj = self.pool.get('purchase.order.line')
        values = {}
        data_line = []
        if purchase_id:        
            order_ids = purchase_order_line_obj.search(cr, uid, [('order_id', '=', purchase_id)], context=context) 
            for line in order_ids:                
                line_data = purchase_order_line_obj.browse(cr, uid, line, context=context)
                product_id = line_data.product_id.id
                description = line_data.product_id.name_template
                quantity = line_data.product_qty
                sequence = line_data.product_id.product_tmpl_id.sequence
                data_line.append({
                                      'sequence':sequence,
                                        'product_id':product_id,
                                         'description': description,
                                        'deliver_quantity':quantity,
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
        
        return self.write(cr, uid, ids, {'state': 'receive', 'receiver_by':uid})
    
    def cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'cancel' })
    
    def check(self, cr, uid, ids, context=None):
#         product_line_obj = self.pool.get('good.receive.note.line')
#         note_obj = self.pool.get('good.receive.note')
#         picking_obj = self.pool.get('stock.picking')
#         move_obj = self.pool.get('stock.move')
#         note_value = req_lines = {}
#         if ids:
#             note_value = note_obj.browse(cr, uid, ids[0], context=context)
#             receive_date = note_value.receive_date
#             location_id = note_value.to_location_id.id
#             from_location_id = note_value.from_location_id.id
#             origin = note_value.name
#             cr.execute('select id from stock_picking_type where default_location_dest_id=%s and name like %s', (location_id, '%Internal Transfer%',))
#             price_rec = cr.fetchone()
#             if price_rec: 
#                 picking_type_id = price_rec[0] 
#             else:
#                 raise osv.except_osv(_('Warning'),
#                                      _('Picking Type has not for this transition'))
#             picking_id = picking_obj.create(cr, uid, {
#                                           'date': receive_date,
#                                           'origin':origin,
#                                           'picking_type_id':picking_type_id}, context=context)
#             note_line_id = product_line_obj.search(cr, uid, [('line_id', '=', ids[0])], context=context)
#             if note_line_id and picking_id:
#                 for id in note_line_id:
#                     note_line_value = product_line_obj.browse(cr, uid, id, context=context)
#                     product_id = note_line_value.product_id.id
#                     name = note_line_value.product_id.name_template
#                     product_uom = note_line_value.product_uom.id
#                     origin = origin
#                     quantity = note_line_value.receive_quantity
#                     big_qty=note_line_value.big_receive_quantity
#                     big_uom=note_line_value.big_uom_id.id
#                     lot_id=note_line_value.batch_no.id
#                     bigger_qty=0
#                     if big_uom:
#                         cr.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (big_uom,))
#                         bigger_qty=cr.fetchone()
#                         if bigger_qty:
#                             bigger_qty=bigger_qty[0]*big_qty
# 
#                         
#                     move_id=move_obj.create(cr, uid, {'picking_id': picking_id,
#                                               'picking_type_id':picking_type_id,
#                                               'restrict_lot_id':lot_id,
#                                           'product_id': product_id,
#                                           'product_uom_qty': quantity+bigger_qty,
#                                           'product_uos_qty': quantity+bigger_qty,
#                                           'product_uom':product_uom,
#                                           'location_id':location_id,
#                                           'location_dest_id':from_location_id,
#                                           'name':name,
#                                            'origin':origin,
#                                           'state':'confirmed'}, context=context)     
#                     move_obj.action_done(cr, uid, move_id, context=context)  
        return self.write(cr, uid, ids, {'state': 'check'})  
                            
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
        
    _columns = {                
        'line_id':fields.many2one('good.receive.note', 'Line', ondelete='cascade', select=True),
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
    }
        
   
    
