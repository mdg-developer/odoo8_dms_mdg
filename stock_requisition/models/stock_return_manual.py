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

class stock_return_manual(osv.osv):
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = "stock.return.manual"
    _description = "Stock Return Manual"
    _order = "id desc"    
    _track = {
        'state': {
            'stock_return_manual.mt_note_confirm': lambda self, cr, uid, obj, ctx = None: obj.state in ['confirm'],
            'stock_return_manual.mt_note_approve': lambda self, cr, uid, obj, ctx = None: obj.state in ['approve']
        },
    }  

    def on_change_sale_team_id(self, cr, uid, ids, sale_team_id, context=None):
        vehicle_id = False
        values = {}
        data_line = []
        if sale_team_id:
            sale_team = self.pool.get('crm.case.section').browse(cr, uid, sale_team_id, context=context)
            issue_warehouse_id = sale_team.issue_warehouse_id.id
            team_warehouse_id = sale_team.warehouse_id.id
            vehicle_id = sale_team.vehicle_id
            if vehicle_id:
                vehicle_id = sale_team.vehicle_id.id
            
            product_line = sale_team.product_ids
            for line in product_line:                
                product = self.pool.get('product.product').browse(cr, uid, line.id, context=context)   
                if product.product_tmpl_id.type == 'product':                                               
                    data_line.append({
                                      'sequence':product.sequence,
                                        'product_id':line.id,
                                         'product_uom': product.product_tmpl_id.uom_id and product.product_tmpl_id.uom_id.id or False,
                                          })
            
            values = {
                 'from_warehouse_id':team_warehouse_id,
                 'to_warehouse_id':issue_warehouse_id ,
                 'vehicle_id':vehicle_id,
                'p_line': data_line,
            }
        return {'value': values}    
         
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
        'name': fields.char('MSRN Ref', readonly=True),
        'from_warehouse_id':fields.many2one('stock.warehouse', 'Returning Warehouse', required=True),
        'to_warehouse_id':fields.many2one('stock.warehouse', 'Receiving Warehouse', required=True),
        'sale_team_id':fields.many2one('crm.case.section', 'Sale Team'),
        'branch_id':fields.many2one('res.branch', 'Branch', required=True),
         'issue_by':fields.char("Issuer"),
       'request_by':fields.many2one('res.users', "Requested By"),
        'approve_by':fields.many2one('res.users', "Approved By"),
        'receiver':fields.char("Receiver"),
        'internal_ref':fields.char("Internal Ref(SIF)"),
         'internal_ref_note' : fields.char('Internal Ref(MRF)'),
         'return_date':fields.date('Date for Return', required=True),
        'vehicle_id':fields.many2one('fleet.vehicle', 'Vehicle No'),
        'state': fields.selection([
            ('draft', 'Pending'),
            ('approve', 'Approved'),
            ('issue', 'Issued'),
            ('cancel', 'Cancel'),
            ('reversed', 'Reversed'),
            
            ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
                 'p_line':fields.one2many('stock.return.manual.line', 'line_id', 'Product Lines',
                              copy=True),
                'company_id':fields.many2one('res.company', 'Company'),
                'partner_id':fields.many2one('res.partner', string='Partner'),
            'issue_from_optional_location':fields.boolean('Return from Optional Location', readonly=False),

}
    _defaults = {
        'state' : 'draft',
         'company_id': _get_default_company,
         'branch_id': _get_default_branch,
    }     
    def create(self, cursor, user, vals, context=None):
        warehouse_id = issue_warehouse_id = vehicle_id = False
        if vals['sale_team_id']:
            sale_team_id = vals['sale_team_id']
            sale_team = self.pool.get('crm.case.section').browse(cursor, user, sale_team_id, context=context)
            issue_warehouse_id = sale_team.issue_warehouse_id.id            
            warehouse_id = sale_team.warehouse_id.id     
            vehicle_id = sale_team.vehicle_id.id        
        id_code = self.pool.get('ir.sequence').get(cursor, user,
                                                'stock.return.manual.code') or '/'
        vals['name'] = id_code
        vals['from_warehouse_id'] = warehouse_id
        vals['to_warehouse_id'] = issue_warehouse_id
        vals['vehicle_id'] = vehicle_id
        
        return super(stock_return_manual, self).create(cursor, user, vals, context=context)
    
    def approve(self, cr, uid, ids, context=None):
        
        return self.write(cr, uid, ids, {'state': 'approve', 'approve_by':uid})
    
    def cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'cancel' })

    def reversed(self, cr, uid, ids, context=None):
        pick_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        stockDetailObj = self.pool.get('stock.transfer_details')
        req_obj = self.pool.get('stock.requisition')
        sale_order_obj = self.pool.get('sale.order')
        detailObj = None
        gin_value = self.browse(cr, uid, ids[0], context=context)
        gin_no = gin_value.name
        pick_ids = []
        pick_ids = pick_obj.search(cr, uid, [('origin', '=', gin_no)], context=context)
        # choose the view_mode accordingly
        for pick_id in pick_ids:
            pick = pick_obj.browse(cr, uid, pick_id, context=context)                
            # Create new picking for returned products
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
                if move.product_uom_qty > 0:
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
                                })
            pick_obj.action_confirm(cr, uid, [new_picking], context=context)
            pick_obj.force_assign(cr, uid, [new_picking], context)  
            wizResult = pick_obj.do_enter_transfer_details(cr, uid, [new_picking], context=context)
            # pop up wizard form => wizResult
            detailObj = stockDetailObj.browse(cr, uid, wizResult['res_id'], context=context)
            if detailObj:
                detailObj.do_detailed_transfer()                                                         
        return self.write(cr, uid, ids, {'state':'reversed'})    
                
    def issue(self, cr, uid, ids, context=None):
        product_line_obj = self.pool.get('stock.return.manual.line')
        note_obj = self.pool.get('stock.return.manual')
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        warehouse_obj = self.pool.get('stock.warehouse')
        note_value = req_lines = {}
        if ids:
            note_value = note_obj.browse(cr, uid, ids[0], context=context)
            return_date = note_value.return_date
            from_warehouse_id = note_value.from_warehouse_id.id
            to_warehouse_id = note_value.to_warehouse_id.id
            if from_warehouse_id:
                from_warehouse_data = warehouse_obj.browse(cr, uid, from_warehouse_id, context=context)
                from_sellable_location_id = from_warehouse_data.lot_stock_id.id
                from_wh_normal_return_location_id = from_warehouse_data.wh_normal_return_location_id.id
                from_wh_exp_location_id = from_warehouse_data.wh_exp_location_id.id
                from_wh_near_exp_location_id = from_warehouse_data.wh_near_exp_location_id.id
                from_wh_damage_location_id = from_warehouse_data.wh_damage_location_id.id
                from_wh_fresh_stock_not_good_location_id = from_warehouse_data.wh_fresh_stock_not_good_location_id.id
                from_wh_temp_location_id = from_warehouse_data.wh_temp_location_id.id    
            if to_warehouse_id:
                to_warehouse_data = warehouse_obj.browse(cr, uid, to_warehouse_id, context=context)
                to_sellable_location_id = to_warehouse_data.lot_stock_id.id
                to_wh_normal_return_location_id = to_warehouse_data.wh_normal_return_location_id.id
                to_wh_exp_location_id = to_warehouse_data.wh_exp_location_id.id
                to_wh_near_exp_location_id = to_warehouse_data.wh_near_exp_location_id.id
                to_wh_damage_location_id = to_warehouse_data.wh_damage_location_id.id
                to_wh_fresh_stock_not_good_location_id = to_warehouse_data.wh_fresh_stock_not_good_location_id.id
                to_wh_temp_location_id = to_warehouse_data.wh_temp_location_id.id                  
                
            origin = note_value.name
            cr.execute('select id from stock_picking_type where default_location_dest_id=%s and name like %s', (from_sellable_location_id, '%Internal Transfer%',))
            price_rec = cr.fetchone()
            if price_rec: 
                picking_type_id = price_rec[0] 
            else:
                raise osv.except_osv(_('Warning'),
                                     _('Picking Type has not for this transition'))
            picking_id = picking_obj.create(cr, uid, {
                                          'date': return_date,
                                          'origin':origin,
                                          'picking_type_id':picking_type_id}, context=context)
            note_line_id = product_line_obj.search(cr, uid, [('line_id', '=', ids[0])], context=context)
            if note_line_id and picking_id:
                for id in note_line_id:
                    note_line_value = product_line_obj.browse(cr, uid, id, context=context)
                    product_id = note_line_value.product_id.id
                    product_uom = note_line_value.product_uom.id
                    origin = origin
                    name = note_line_value.product_id.name_template
                    if note_line_value.sellable_quantity > 0:
                        quantity = note_line_value.sellable_quantity
                        location_id = from_sellable_location_id
                        to_location_id = to_sellable_location_id
                        move_id = move_obj.create(cr, uid, {'picking_id': picking_id,
                                                  'picking_type_id':picking_type_id,
                                              'product_id': product_id,
                                              'product_uom_qty': quantity,
                                              'product_uos_qty': quantity,
                                              'product_uom':product_uom,
                                              'location_id':location_id,
                                              'location_dest_id':to_location_id,
                                              'name':name,
                                               'origin':origin,
                                              'state':'confirmed'}, context=context)     
                        move_obj.action_done(cr, uid, move_id, context=context)  
                    if note_line_value.normal_return_quantity > 0:
                        quantity = note_line_value.normal_return_quantity
                        location_id = from_wh_normal_return_location_id
                        to_location_id = to_wh_normal_return_location_id
                        move_id = move_obj.create(cr, uid, {'picking_id': picking_id,
                                                  'picking_type_id':picking_type_id,
                                              'product_id': product_id,
                                              'product_uom_qty': quantity,
                                              'product_uos_qty': quantity,
                                              'product_uom':product_uom,
                                              'location_id':location_id,
                                              'location_dest_id':to_location_id,
                                              'name':name,
                                               'origin':origin,
                                              'state':'confirmed'}, context=context)     
                        move_obj.action_done(cr, uid, move_id, context=context)      
                    if note_line_value.exp_quantity > 0:
                        quantity = note_line_value.exp_quantity
                        location_id = from_wh_exp_location_id
                        to_location_id = to_wh_exp_location_id
                        move_id = move_obj.create(cr, uid, {'picking_id': picking_id,
                                                  'picking_type_id':picking_type_id,
                                              'product_id': product_id,
                                              'product_uom_qty': quantity,
                                              'product_uos_qty': quantity,
                                              'product_uom':product_uom,
                                              'location_id':location_id,
                                              'location_dest_id':to_location_id,
                                              'name':name,
                                               'origin':origin,
                                              'state':'confirmed'}, context=context)     
                        move_obj.action_done(cr, uid, move_id, context=context) 
                    if note_line_value.near_exp_quantity > 0:
                        quantity = note_line_value.near_exp_quantity
                        location_id = from_wh_near_exp_location_id
                        to_location_id = to_wh_near_exp_location_id
                        move_id = move_obj.create(cr, uid, {'picking_id': picking_id,
                                                  'picking_type_id':picking_type_id,
                                              'product_id': product_id,
                                              'product_uom_qty': quantity,
                                              'product_uos_qty': quantity,
                                              'product_uom':product_uom,
                                              'location_id':location_id,
                                              'location_dest_id':to_location_id,
                                              'name':name,
                                               'origin':origin,
                                              'state':'confirmed'}, context=context)     
                        move_obj.action_done(cr, uid, move_id, context=context)       
                    if note_line_value.damage_quantity > 0:
                        quantity = note_line_value.damage_quantity
                        location_id = from_wh_damage_location_id
                        to_location_id = to_wh_damage_location_id
                        move_id = move_obj.create(cr, uid, {'picking_id': picking_id,
                                                  'picking_type_id':picking_type_id,
                                              'product_id': product_id,
                                              'product_uom_qty': quantity,
                                              'product_uos_qty': quantity,
                                              'product_uom':product_uom,
                                              'location_id':location_id,
                                              'location_dest_id':to_location_id,
                                              'name':name,
                                               'origin':origin,
                                              'state':'confirmed'}, context=context)     
                        move_obj.action_done(cr, uid, move_id, context=context)       
                    if note_line_value.fresh_quantity > 0:
                        quantity = note_line_value.fresh_quantity
                        location_id = from_wh_fresh_stock_not_good_location_id
                        to_location_id = to_wh_fresh_stock_not_good_location_id
                        move_id = move_obj.create(cr, uid, {'picking_id': picking_id,
                                                  'picking_type_id':picking_type_id,
                                              'product_id': product_id,
                                              'product_uom_qty': quantity,
                                              'product_uos_qty': quantity,
                                              'product_uom':product_uom,
                                              'location_id':location_id,
                                              'location_dest_id':to_location_id,
                                              'name':name,
                                               'origin':origin,
                                              'state':'confirmed'}, context=context)     
                        move_obj.action_done(cr, uid, move_id, context=context)                                                       
                    if note_line_value.temp_quantity > 0:
                        quantity = note_line_value.temp_quantity
                        location_id = from_wh_temp_location_id
                        to_location_id = to_wh_temp_location_id
                        move_id = move_obj.create(cr, uid, {'picking_id': picking_id,
                                                  'picking_type_id':picking_type_id,
                                              'product_id': product_id,
                                              'product_uom_qty': quantity,
                                              'product_uos_qty': quantity,
                                              'product_uom':product_uom,
                                              'location_id':location_id,
                                              'location_dest_id':to_location_id,
                                              'name':name,
                                               'origin':origin,
                                              'state':'confirmed'}, context=context)     
                        move_obj.action_done(cr, uid, move_id, context=context)                                                       
                                                                                                                                                                            
                    cr.execute('''update stock_move set date=((%s::date)::text || ' ' || date::time(0))::timestamp where state='done' and origin =%s''', (return_date, origin,))

        return self.write(cr, uid, ids, {'state': 'issue'})  
                            
class stock_return_manual_line(osv.osv):  # #prod_pricelist_update_line
    _name = 'stock.return.manual.line'
    _description = 'Note Line'

    def on_change_product_id(self, cr, uid, ids, product_id, context=None):
        values = {}
        domain = {}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            values = {
                'product_uom': product.product_tmpl_id.uom_id and product.product_tmpl_id.uom_id.id or False,
            }
            cr.execute("""SELECT uom.id FROM product_product pp 
                          LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                          LEFT JOIN product_template_product_uom_rel rel ON (rel.product_template_id=pt.id)
                          LEFT JOIN product_uom uom ON (rel.product_uom_id=uom.id)
                          WHERE pp.id = %s""", (product.id,))
            uom_list = cr.fetchall()
            domain = {'product_uom': [('id', 'in', uom_list)]}
        return {'value': values, 'domain':domain}
    def create(self, cr, uid, data, context=None):
        product = data['product_id']
        if product:
#             if type(product)==str:
#                 product=int(product)
            product_data = self.pool.get('product.product').browse(cr, uid, product, context=context)
            uom_id = product_data.uom_id.id
            data['product_uom'] = uom_id
        return super(stock_return_manual_line, self).create(cr, uid, data, context=context)            
    _columns = {                
        'line_id':fields.many2one('stock.return.manual', 'Line', ondelete='cascade', select=True),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'sellable_quantity' : fields.float(string='Sellable', digits=(16, 0)),
        'normal_return_quantity' : fields.float(string='Normal Return', digits=(16, 0)),
        'exp_quantity' : fields.float(string='Expiry', digits=(16, 0)),
        'near_exp_quantity' : fields.float(string='Near Expiry', digits=(16, 0)),
        'damage_quantity' : fields.float(string='Damage', digits=(16, 0)),
        'fresh_quantity' : fields.float(string='Fresh Not Good', digits=(16, 0)),
        'temp_quantity' : fields.float(string='Temp', digits=(16, 0)),
        'product_uom': fields.many2one('product.uom', 'UoM', readonly=True),
        'remark':fields.char('Remark'),
        'sequence':fields.integer('Sequence'),
    }
        
   
    
