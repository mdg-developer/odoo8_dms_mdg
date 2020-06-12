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

class good_issue_note(osv.osv):
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = "good.issue.note"
    _description = "Good Issue Note"
    _order = "id desc"    
    _track = {
        'state': {
            'good_issue_note.mt_note_confirm': lambda self, cr, uid, obj, ctx = None: obj.state in ['confirm'],
            'good_issue_note.mt_note_approve': lambda self, cr, uid, obj, ctx = None: obj.state in ['approve']
        },
    }  
#     
#     def _get_default_branch(self, cr, uid, context=None):
#         branch_id = self.pool.get('res.users')._get_branch(cr, uid, context=context)
#         if not branch_id:
#             raise osv.except_osv(_('Error!'), _('There is no default branch for the current user!'))
#         return branch_id
        
      
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id   
    
    _columns = {
        'name': fields.char('GIN Ref', readonly=True),
        'request_id':fields.many2one('stock.requisition', 'RFI Ref', readonly=True),
        'to_location_id':fields.many2one('stock.location', 'Requesting Location', required=True),
        'from_location_id':fields.many2one('stock.location', 'Request Warehouse', required=True),
        'sale_team_id':fields.many2one('crm.case.section', 'Delivery Team'),
     #   'branch_id':fields.many2one('res.branch', 'Branch',required=True),
#         'so_no' : fields.char('Sales Order/Inv Ref;No.'),
         'issue_by':fields.char("Issuer"),
       'request_by':fields.many2one('res.users', "Requested By"),
        'approve_by':fields.many2one('res.users', "Approved By"),
        'receiver':fields.char("Receiver"),
        'internal_ref':fields.char("Internal Ref"),
       
#         'request_date' : fields.date('Date internal_refRequested'),
         'issue_date':fields.date('Date for Issue',required=True),
        'vehicle_id':fields.many2one('fleet.vehicle', 'Vehicle No'),
        'state': fields.selection([
            ('draft', 'Pending'),
            ('approve', 'Approved'),
            ('issue','Issued'),
            ('cancel', 'Cancel'),
            ('reversed', 'Reversed'),
            
            ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
                 'p_line':fields.one2many('good.issue.note.line', 'line_id', 'Product Lines',
                              copy=True),
                'company_id':fields.many2one('res.company', 'Company'),
                'partner_id':fields.many2one('res.partner', string='Partner'),
                'is_return':fields.boolean('Return'),
                'issue_from_optional_location':fields.boolean('Issue from Optional Location',readonly=True),
                'reverse_date':fields.date('Date for Reverse',required=False),
                'reverse_user_id':fields.many2one('res.users', "Reverse User"),
                'sub_d_customer_id':fields.many2one('sub.d.customer', 'Sub-D Customer'), 
                    'principle_id'    :fields.many2one('product.maingroup', 'Principle'),
               
}
    _defaults = {
        'state' : 'draft',
         'company_id': _get_default_company,
        # 'branch_id': _get_default_branch,
         'is_return':False,
         
    }     
    def create(self, cursor, user, vals, context=None):
        id_code = self.pool.get('ir.sequence').get(cursor, user,
                                                'good.issue.note.code') or '/'
        vals['name'] = id_code
        return super(good_issue_note, self).create(cursor, user, vals, context=context)
    
    def approve(self, cr, uid, ids, context=None):
        
        return self.write(cr, uid, ids, {'state': 'approve','approve_by':uid})
    
    def cancel(self, cr, uid, ids, context=None):
        req_obj = self.pool.get('stock.requisition')
        sale_order_obj = self.pool.get('sale.order')
        req_id = req_obj.search(cr, uid, [('good_issue_id', '=', ids[0])], context=context)
        req_value = req_obj.browse(cr, uid, req_id, context=context)
        for order in req_value.order_line:
            so_name = order.name
            order_id = sale_order_obj.search(cr, uid, [('name', '=', so_name)], context=context) 
            sale_order_obj.write(cr, uid, order_id, {'is_generate':False})    
        print 'res'
        req_obj.write(cr, uid, req_id, {'state':'cancel'})    
        return self.write(cr, uid, ids, {'state':'cancel' })

    def reversed(self, cr, uid, ids, context=None):
        pick_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        stockDetailObj = self.pool.get('stock.transfer_details')
        req_obj = self.pool.get('stock.requisition')
        sale_order_obj = self.pool.get('sale.order')
        detailObj = None
        gin_value = self.browse(cr, uid, ids[0], context=context)
        gin_no=gin_value.name
        reverse_date=gin_value.reverse_date
        if not reverse_date:
            raise osv.except_osv(_('Warning'),
                     _('Please Insert Reverse Date'))
        pick_ids = []
        pick_ids = pick_obj.search(cr, uid, [('origin', '=', gin_no)], context=context)
        #choose the view_mode accordingly
        for pick_id in pick_ids:
            pick = pick_obj.browse(cr, uid, pick_id, context=context)                
            #Create new picking for returned products
            pick_type_id = pick.picking_type_id.return_picking_type_id and pick.picking_type_id.return_picking_type_id.id or pick.picking_type_id.id
            new_picking = pick_obj.copy(cr, uid, pick.id, {
                'move_lines': [],
                'picking_type_id': pick_type_id,
                'state': 'draft',
                'origin': pick.name,
            }, context=context)
            for move in pick.move_lines:
                if move.origin_returned_move_id.move_dest_id.id and move.origin_returned_move_id.move_dest_id.state != 'cancel':
                    move_dest_id = move.origin_returned_move_id.move_dest_id.id
                else:
                    move_dest_id = False
                if move.product_uom_qty >0:
                    move_obj.copy(cr, uid, move.id, {
                                        'product_id': move.product_id.id,
                                        'product_uom_qty': move.product_uom_qty,
                                        'product_uos_qty': move.product_uom_qty * move.product_uos_qty / move.product_uom_qty,
                                        'picking_id': new_picking,
                                        'state': 'draft',
                                        'location_id': move.location_dest_id.id,
                                        'location_dest_id': move.location_id.id,
                                        'picking_type_id': pick_type_id,
                                        'warehouse_id': pick.picking_type_id.warehouse_id.id,
                                        'origin_returned_move_id': move.id,
                                        'procure_method': 'make_to_stock',
                                      #  'restrict_lot_id': data_get.lot_id.id,
                                        'move_dest_id': move_dest_id,
                                        'origin':'Reverse ' + move.origin,
                                })
            pick_obj.action_confirm(cr, uid, [new_picking], context=context)
            pick_obj.force_assign(cr, uid, [new_picking], context)  
            wizResult = pick_obj.do_enter_transfer_details(cr, uid, [new_picking], context=context)
            # pop up wizard form => wizResult
            detailObj = stockDetailObj.browse(cr, uid, wizResult['res_id'], context=context)
            if detailObj:
                detailObj.do_detailed_transfer()
            cr.execute("update stock_move set date=%s where origin=%s", (reverse_date, 'Reverse ' +move.origin,))

        req_id = req_obj.search(cr, uid, [('good_issue_id', '=', ids[0])], context=context)
        req_value = req_obj.browse(cr, uid, req_id, context=context)
        for order in req_value.order_line:
            so_name = order.name
            order_id = sale_order_obj.search(cr, uid, [('name', '=', so_name)], context=context) 
            sale_order_obj.write(cr, uid, order_id, {'is_generate':False})    
        req_obj.write(cr, uid, req_id, {'state':'reversed'})                                                              
        return self.write(cr, uid, ids, {'state':'reversed','reverse_user_id':uid})    
    
#     def unlink(self, cr, uid, ids, context=None):
#         good_issue_notes = self.read(cr, uid, ids, ['state'], context=context)
#         unlink_ids = []
#         for s in good_issue_notes:
#             if s['state'] in ['draft','approve', 'cancel']:
#                 unlink_ids.append(s['id'])
#             else:
#                 raise osv.except_osv(_('Invalid Action!'), _('You cannot cancel the issued Good Issue Note!'))
# 
#         return super(good_issue_notes, self).unlink(cr, uid, unlink_ids, context=context)

    def updateQtyOnHand(self, cr, uid, ids, context=None):
        product_line_obj = self.pool.get('good.issue.note.line')
        if ids:
            note_data = self.browse(cr, uid, ids[0], context=context)
            location_id = note_data.to_location_id.id
            req_line_id = product_line_obj.search(cr, uid, [('line_id', '=', ids[0])], context=context)
            for data in req_line_id:
                note_line_value = product_line_obj.browse(cr, uid, data, context=context)
                line_id= note_line_value.id
                product_id = note_line_value.product_id.id
                cr.execute('select  SUM(COALESCE(qty,0)) qty from stock_quant where location_id=%s and product_id=%s and qty >0 group by product_id', (location_id, product_id,))
                qty_on_hand = cr.fetchone()
                if qty_on_hand:
                    qty_on_hand = qty_on_hand[0]
                else:
                    qty_on_hand = 0
                cr.execute("update good_issue_note_line set qty_on_hand=%s where product_id=%s and id=%s", (qty_on_hand, product_id,line_id,))
            
    def issue(self, cr, uid, ids, context=None):
        product_line_obj = self.pool.get('good.issue.note.line')
        note_obj = self.pool.get('good.issue.note')
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        note_value = req_lines = {}
        current_note_obj = note_obj.browse(cr, uid, ids[0], context=context)
        request_order_line = current_note_obj.request_id.order_line
        sale_order_obj = self.pool.get('sale.order')
        if ids:
            note_value= note_obj.browse(cr, uid, ids[0], context=context)
            issue_date = note_value.issue_date
            location_id = note_value.to_location_id.id
            from_location_id = note_value.from_location_id.id
            origin = note_value.name
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
                    quant_note_line_value = product_line_obj.browse(cr, uid, id, context=context)
                    quant_product_id = quant_note_line_value.product_id.id
                    cr.execute('''select a.qty_on_hand,sum(a.total_issue_qty) as total_issue_qty from (
                      select (select COALESCE (sum(qty),0) from stock_quant where product_id =line.product_id and location_id = note.to_location_id)  as qty_on_hand,
                      line.product_id,line.issue_quantity as issue_quantity,
                      (line.issue_quantity*(select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=product_uom) )as total_issue_qty 
                      from good_issue_note_line line,good_issue_note note
                      where  line.line_id=note.id and line.product_id =%s 
                      and note.id=%s
                      )a
                      group by product_id,qty_on_hand''',(quant_product_id,note_value.id,))
                    note_data=cr.fetchone()
                    if note_data:
                        qty_on_hand=note_data[0]
                        total_issue_qty=note_data[1]
                    product_check_data = self.pool.get('product.product').browse(cr, uid, quant_product_id, context=context)   
                    if qty_on_hand < total_issue_qty:
                        raise osv.except_osv(_('Warning'),
                                 _('Please Check Qty On Hand For (%s)') % (product_check_data.name_template,))

                for id in note_line_id:
                    note_line_value = product_line_obj.browse(cr, uid, id, context=context)
                    product_id = note_line_value.product_id.id
                    name = note_line_value.product_id.name_template
                    product_uom = note_line_value.product_uom.id
                    origin = origin
                    quantity = note_line_value.issue_quantity
                    big_qty=note_line_value.big_issue_quantity
                    big_uom=note_line_value.big_uom_id.id
                    lot_id=note_line_value.batch_no.id

                    
                    #comment by EMTW
#                     bigger_qty=0
#                     if big_uom:
#                         cr.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (big_uom,))
#                         bigger_qty=cr.fetchone()
#                         if bigger_qty:
#                             bigger_qty=bigger_qty[0]*big_qty
                        
                    move_id=move_obj.create(cr, uid, {'picking_id': picking_id,
                                              'picking_type_id':picking_type_id,
                                              'restrict_lot_id':lot_id,
                                          'product_id': product_id,
                                          'product_uom_qty': quantity,
                                          'product_uos_qty': quantity,
                                          'product_uom':product_uom,
                                          'location_id':location_id,
                                          'location_dest_id':from_location_id,
                                          'name':name,
                                           'origin':origin,
                                          'state':'confirmed'}, context=context)     
                    move_obj.action_done(cr, uid, move_id, context=context)  
                    cr.execute('''update stock_move set date=((%s::date)::text || ' ' || date::time(0))::timestamp where state='done' and origin =%s''',(issue_date,origin,))
        result = self.write(cr, uid, ids, {'state': 'issue'})
        if result:
            for line in request_order_line:
                order_ids = sale_order_obj.search(cr, uid, [('name', '=', line.name)], context=context)
                current_order = sale_order_obj.browse(cr, uid, order_ids[0], context=context)
                if current_order:
                    current_order.update_woo_order_status_action('delivered')                    
        return result  
                            
class good_issue_line(osv.osv):  # #prod_pricelist_update_line
    _name = 'good.issue.note.line'
    _description = 'Note Line'

    def on_change_product_id(self, cr, uid, ids, product_id, context=None):
        values = {}
        domain={}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            values = {
                      'big_uom_id':product.product_tmpl_id.uom_id and product.product_tmpl_id.uom_id.id or False,
                'product_uom': product.product_tmpl_id.uom_id and product.product_tmpl_id.uom_id.id or False,
                'uom_ratio': product.product_tmpl_id.uom_ratio,
            }
            cr.execute("""SELECT uom.id FROM product_product pp 
                          LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                          LEFT JOIN product_template_product_uom_rel rel ON (rel.product_template_id=pt.id)
                          LEFT JOIN product_uom uom ON (rel.product_uom_id=uom.id)
                          WHERE pp.id = %s""", (product.id,))
            uom_list = cr.fetchall()
            domain = {'product_uom': [('id', 'in', uom_list)]}
            
        return {'value': values,'domain':domain}
    
    def on_change_expired_date(self, cr, uid, ids, batch_no, context=None):
        values = {}
        if batch_no:
            lot_obj = self.pool.get('stock.production.lot').browse(cr, uid, batch_no, context=context)
            values = {
                'expiry_date': lot_obj.life_date,
            }
        return {'value': values}    
        
    _columns = {                
        'line_id':fields.many2one('good.issue.note', 'Line', ondelete='cascade', select=True),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'issue_quantity' : fields.float(string='Qty', digits=(16, 0)),
        'product_uom': fields.many2one('product.uom', 'Smaller UoM'),
                'uom_ratio':fields.char('Packing Unit'),
                'batch_no':fields.many2one('stock.production.lot','Batch No'),
                'expiry_date':fields.date('Expiry'),
                 'remark':fields.char('Remark'),
        'big_uom_id': fields.many2one('product.uom', 'Bigger UoM', help="Default Unit of Measure used for all stock operation."),
        'big_issue_quantity' : fields.float(string='Qty', digits=(16, 0)),               
         'qty_on_hand':fields.float(string='Qty On Hand', digits=(16, 0),readonly=True),
        'sequence':fields.integer('Sequence'),
        'opening_qty':fields.float('Opening Qty',readonly=True, digits=(16, 0)),
        'opening_product_uom': fields.many2one('product.uom', 'Opening UoM',readonly=True, digits=(16, 0)),

    }
        
   
    
