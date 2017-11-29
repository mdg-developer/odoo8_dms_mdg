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


class stock_return(osv.osv_memory):
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = "stock.return"
    _description = "Stock Return"
    _order = "id desc"    
    _track = {
        'state': {
            'stock_return.mt_return_confirm': lambda self, cr, uid, obj, ctx = None: obj.state in ['confirm'],
            'stock_return.mt_return_approve': lambda self, cr, uid, obj, ctx = None: obj.state in ['approve']
        },
    }    
    
    def on_change_sale_team_id(self, cr, uid, ids, sale_team_id, context=None):
        values = {}
        team_obj = self.pool.get('crm.case.section')
        if sale_team_id:
            team = team_obj.browse(cr, uid, sale_team_id, context=context)
            values = {
                'vehicle_id': team.vehicle_id and team.vehicle_id.id or False,
                'from_location':team.location_id,
                'from_return_location':team.return_location_id,
                'returner':team.receiver,
            }
        return {'value': values}
    
    def on_change_warehouse_id(self, cr, uid, ids, warehouse_id, context=None):
        values = {}
        warehouse_obj = self.pool.get('stock.warehouse')
        if warehouse_id:
            warehouse = warehouse_obj.browse(cr, uid, warehouse_id, context=context)
            values = {
                'to_location': warehouse.lot_stock_id,
                'to_return_location':warehouse.return_location_id,
            }
        return {'value': values}
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id   
    
    
    def retrieve_data(self, cr, uid, ids, context=None):
        product_trans_obj = self.pool.get('product.transactions')
        product_trans_line_obj = self.pool.get('product.transactions.line')
        mobile_obj = self.pool.get('stock.return.mobile')
        stock_return_obj = self.pool.get('stock.return.line')
        product_obj = self.pool.get('product.product')
        quant_obj = self.pool.get('stock.quant')

        
        if ids:
            cr.execute('delete from stock_return_line where line_id=%s', (ids[0],))
            return_data = self.browse(cr, uid, ids, context=context)
            return_date = return_data.return_date
            from_location_id = return_data.from_location.id
            from_return_location_id = return_data.from_return_location.id            
            sale_team_id = return_data.sale_team_id.id
            car_quant_ids = quant_obj.search(cr, uid, [('location_id', '=', from_location_id)])
            if  car_quant_ids:        
                for quant_id in car_quant_ids:
                    quant_data = quant_obj.browse(cr, uid, quant_id, context=context)
                    product_id = quant_data.product_id.id
                    product_data = product_obj.browse(cr, uid, product_id, context=context)
                    sequence = product_data.sequence
                    uom_id = product_data.uom_id.id
                    default_code = product_data.product_tmpl_id.default_code
                    quantity = quant_data.qty
                    stock_id = stock_return_obj.search(cr, uid, [('line_id', '=', ids[0]) , ('product_id', '=', product_id), ('status', '=', 'Stock Return')])
                    print 'stock_idstock_idstock_id ,stock_id', stock_id
                    if  stock_id:
                        cr.execute('update stock_return_line set onhand_quantity =onhand_quantity+ %s where id=%s ', (quantity, stock_id[0],))
                    else:   
                        stock_return_obj.create(cr, uid, {'line_id': ids[0],
                                                     'sequence':sequence,
                                                  'product_id': product_id,
                                                  'product_code': default_code,
                                                  'product_uom': uom_id,
                                                  'status':'Stock Return',
                                                  'onhand_quantity':quantity,
                                                  'actual_quantity':0,
                                                  'return_quantity':0,
                                                  'closing_quantity':0,
                                                }, context=context)
                    
            return_quant_ids = quant_obj.search(cr, uid, [('location_id', '=', from_return_location_id)])
            if  return_quant_ids:        
                for quant_id in return_quant_ids:
                    quant_data = quant_obj.browse(cr, uid, quant_id, context=context)
                    product_id = quant_data.product_id.id
                    product_data = product_obj.browse(cr, uid, product_id, context=context)
                    sequence = product_data.sequence
                    uom_id = product_data.uom_id.id
                    default_code = product_data.product_tmpl_id.default_code
                    quantity = quant_data.qty
                    return_stock_id = stock_return_obj.search(cr, uid , [('line_id', '=', ids[0]) , ('product_id', '=', product_id), ('status', '=', 'Sale Return')])
                    if  return_stock_id:
                        cr.execute('update stock_return_line set onhand_quantity =onhand_quantity+ %s where id=%s ', (quantity, return_stock_id[0],))
                    else:                       
                        stock_return_obj.create(cr, uid, {'line_id': ids[0],
                                                     'sequence':sequence,
                                                  'product_id': product_id,
                                                  'product_code': default_code,
                                                  'product_uom': uom_id,
                                                  'status':'Sale Return',
                                                  'onhand_quantity':quantity,
                                                  'actual_quantity':0,
                                                  'return_quantity':0,
                                                  'closing_quantity':0,
                                                }, context=context)
        return True 
        
    def _get_default_branch(self, cr, uid, context=None):
        branch_id = self.pool.get('res.users')._get_branch(cr, uid, context=context)
        if not branch_id:
            raise osv.except_osv(_('Error!'), _('There is no default branch for the current user!'))
        return branch_id 
        
    _columns = {
        'sale_team_id':fields.many2one('crm.case.section', 'Sales Team' , required=True),
        'name': fields.char('SRN Ref', readonly=True),
        'note_id':fields.many2one('good.issue.note', '(GIN)Ref;No.'),
        'from_location':fields.many2one('stock.location', 'From Location'),
        'from_return_location':fields.many2one('stock.location', 'From Return Location'),
         'warehouse_id':fields.many2one('stock.warehouse', 'Warehouse'),
        'to_location':fields.many2one('stock.location', 'To Location'),
        'to_return_location':fields.many2one('stock.location', 'To Return Location', store=True),
        'return_from':fields.char('Return From'),
         'so_no' : fields.char('Sales Order/Inv Ref;No.'),
         'returner' : fields.char('Returned By'),
         'wh_receiver' : fields.char('WH Receiver'),
         'return_date':fields.date('Date of Return', required=True),
         'vehicle_id':fields.many2one('fleet.vehicle', 'Vehicle No'),
#         'branch_id':fields.many2one('res.branch', 'Branch'),
         'state': fields.selection([
            ('draft', 'Pending'),
            ('received', 'Received'),
            ('cancel', 'Cancel')
            ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
        'p_line':fields.one2many('stock.return.line', 'line_id', 'Product Lines',
                              copy=True),
                'company_id':fields.many2one('res.company', 'Company'),
				'partner_id':fields.many2one('res.partner', 'Customer'),
}		
    
    _defaults = {
        'state' : 'draft',
         'company_id': _get_default_company,
         'branch_id': _get_default_branch,
         'return_date' :fields.datetime.now
    }     
    
    def create(self, cursor, user, vals, context=None):
        if vals['warehouse_id']:
            warehouse_id = vals['warehouse_id']
            warehouse_data = self.pool.get('stock.warehouse').browse(cursor, user, warehouse_id, context=context)
            to_location_id = warehouse_data.lot_stock_id.id            
            from_location_id = warehouse_data.return_location_id.id
        id_code = self.pool.get('ir.sequence').get(cursor, user,
                                                'stock.return.code') or '/'
        vals['name'] = id_code
        vals['to_location'] = to_location_id
        vals['to_return_location'] = from_location_id        
        return super(stock_return, self).create(cursor, user, vals, context=context)
    

    
    def confirm(self, cr, uid, ids, context=None):        
        return self.write(cr, uid, ids, {'state': 'confirm', })
    
    def cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel', })
    
    def received(self, cr, uid, ids, context=None):
        partner_obj = self.pool.get('res.partner')
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')     
        location_obj = self.pool.get('stock.location')     
              
        return_obj = self.browse(cr, uid, ids, context=context)    
        team_location_id = return_obj.sale_team_id.location_id.id
        return_location_id = return_obj.sale_team_id.return_location_id.id
        tmp_location_id = return_obj.sale_team_id.temp_location_id.id
        origin = return_obj.name
        main_location_id = return_obj.to_location.id    
        to_return_location_id = return_obj.to_return_location.id    
        for line in return_obj.p_line:
            product_id = line.product_id.id
            name = line.product_id.name_template          
            onhand_quantity = line.onhand_quantity
            actual_quantity = line.actual_quantity
            return_quantity = line.return_quantity
            uom_id = line.product_uom.id
            if  line.status == 'Stock Return':
                different_qty = 0
                different_qty = onhand_quantity - actual_quantity
                cr.execute("update stock_return_line set different_qty= %s where id=%s", (different_qty, line.id,))            
                if different_qty:
                    if different_qty < 0:
                        # Tmp===> Car
                        inventory_location_id = location_obj.search(cr, uid, [('name', '=', 'Inventory loss')])
                        move_id = move_obj.create(cr, uid, {
                                              'product_id': product_id,
                                              'product_uom_qty':-1 * different_qty ,
                                              'product_uos_qty':-1 * different_qty,
                                              'product_uom':uom_id,
                                              'location_id':inventory_location_id[0],
                                              'location_dest_id':tmp_location_id,
                                              'name':name,
                                               'origin':origin,
                                               'manual':True,
                                              'state':'confirmed'}, context=context)     
                        move_obj.action_done(cr, uid, move_id, context=context)
                    if different_qty > 0:
    #                         Car===> tmp                    
                        move_id = move_obj.create(cr, uid, {
                                              'product_id': product_id,
                                              'product_uom_qty':  different_qty ,
                                              'product_uos_qty':  different_qty,
                                              'product_uom':uom_id,
                                              'location_id':team_location_id,
                                              'location_dest_id':tmp_location_id,
                                              'name':name,
                                               'origin':origin,
                                             'manual':True,
                                              'state':'confirmed'}, context=context)     
                        move_obj.action_done(cr, uid, move_id, context=context)        
                if return_quantity > 0:
                    #                         Car===> To Location                    
                        move_id = move_obj.create(cr, uid, {
                                              'product_id': product_id,
                                              'product_uom_qty':  return_quantity ,
                                              'product_uos_qty':  return_quantity,
                                              'product_uom':uom_id,
                                              'location_id':team_location_id,
                                              'location_dest_id':main_location_id,
                                              'name':name,
                                               'origin':origin,
                                             'manual':True,
                                              'state':'confirmed'}, context=context)     
                        move_obj.action_done(cr, uid, move_id, context=context)   
            if  line.status == 'Sale Return':
                if return_quantity > 0:
                    #                         Car Return===> To Retun Location                    
                        move_id = move_obj.create(cr, uid, {
                                              'product_id': product_id,
                                              'product_uom_qty':  return_quantity ,
                                              'product_uos_qty':  return_quantity,
                                              'product_uom':uom_id,
                                              'location_id':return_location_id,
                                              'location_dest_id':to_return_location_id,
                                              'name':name,
                                               'origin':origin,
                                             'manual':True,
                                              'state':'confirmed'}, context=context)     
                        move_obj.action_done(cr, uid, move_id, context=context)                                                                

        return self.write(cr, uid, ids, {'state':'received'})    

            
class stock_return_line(osv.osv):  # #prod_pricelist_update_line
    _name = 'stock.return.line'
    _description = 'Return Line'
    def on_change_return_quantity(self, cr, uid, ids, actual_quantity, return_quantity, context=None):
        values = {}
        if actual_quantity:
            closing_qty = actual_quantity - return_quantity
            values = {
                'closing_quantity': closing_qty,
            }
        return {'value': values}            
    _columns = {                
        'line_id':fields.many2one('stock.return', 'Line', ondelete='cascade', select=True),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'product_code': fields.char('Product Code'),
        'status': fields.char('Status'),
        'onhand_quantity' : fields.float(string='Theorectical Qty', digits=(16, 2)),
        'actual_quantity' : fields.float(string='Actual Qty', digits=(16, 2)),
        'return_quantity' : fields.float(string='Return Qty', digits=(16, 2)),
        'closing_quantity':fields.float(string='Closing Qty', digits=(16, 2)),
        'sequence':fields.integer('Sequence'),
        'different_qty':fields.float(string='Different Qty', digits=(16, 2)), #fields.integer('Different Qty'),
         'remark':fields.char('Remark'),
#         'sale_quantity' : fields.float(string='Sales Qty', digits=(16, 0)),
#         'sale_quantity_big' : fields.float(string='Sales Qty Big', digits=(16, 0)),
#         'foc_quantity' : fields.float(string='FOC Qty', digits=(16, 0)),        
         'product_uom': fields.many2one('product.uom', 'UOM', required=True),
#         'uom_ratio':fields.char('Packing Unit'),
#         'expiry_date':fields.date('Expiry'),
#         'rec_big_uom_id': fields.many2one('product.uom', 'Rec Bigger UoM',help="Default Unit of Measure used for all stock operation."),
#         'rec_big_quantity' : fields.float(string='Rec Qty', digits=(16, 0)),        
#         'rec_small_quantity' : fields.float(string='Rec Small Qty', digits=(16, 0)),
#         'rec_small_uom_id': fields.many2one('product.uom', 'Rec Smaller UoM'),         


    }
        
   
    
