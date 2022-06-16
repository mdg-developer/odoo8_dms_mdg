'''
Created on Auguest 31, 2016

@author: Administrator
'''
import time

import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from dateutil import parser
import time
from openerp.osv import fields , osv
from openerp.tools.translate import _
import datetime
import math
from datetime import datetime, date, time
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as OE_DATETIMEFORMAT

class stock_taking(osv.osv):
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = "stock.taking"
    _description = "Stock Taking"
    _order = "id desc"    
    _track = {
        'state': {
            'stock_taking.mt_stock_taking_confirm': lambda self, cr, uid, obj, ctx = None: obj.state in ['confirm'],
            'stock_taking.mt_stock_taking_approve': lambda self, cr, uid, obj, ctx = None: obj.state in ['approve']
        },
    }        
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id     
    
    _columns = {
        'name': fields.char('STLI Ref', readonly=True),
        'transfer_id':fields.many2one('stock.transfer.request', 'TR.Ref No', required=True),
        'from_warehouse_id':fields.many2one('stock.warehouse', 'Request From', required=True),
        'to_warehouse_id':fields.many2one('stock.warehouse', 'Issue From', required=True),
        'issue_to':fields.many2one('res.users', "Issue To" , readonly=True),
        'taken_by':fields.many2one('res.users', "Stock Taken By", readonly=True),
        'loading_by':fields.many2one('res.users', "Loading By", readonly=True),
        'issue_date' : fields.date('Issue Date'),
        'operation_date' : fields.date('Operation Date'),
        'gin_no': fields.char('GIN Ref;'),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('issue', 'Issued'),
            ('taken', 'Stock Taken'),
            ('loaded', 'Loaded'),
            ('cancel', 'Cancel'),
            ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
        'p_line':fields.one2many('stock.taking.line', 'line_id', 'Product Lines',
                              copy=True),
    'company_id':fields.many2one('res.company', 'Company'),
     'partner_id':fields.many2one('res.partner', string='Partner'),

}
    _defaults = {
        'state' : 'draft',
         'company_id': _get_default_company,
         'issue_date': fields.datetime.now,
        'operation_date': fields.datetime.now,

    }     
    
    def create(self, cursor, user, vals, context=None):
        id_code = self.pool.get('ir.sequence').get(cursor, user,
                                                'stock.taking.code') or '/'
        vals['name'] = id_code
        return super(stock_taking, self).create(cursor, user, vals, context=context)
    
    def on_change_transfer_id(self, cr, uid, ids, transfer_id, from_warehouse_id, context=None):
        transfer_obj = self.pool.get('stock.transfer.request')      
        picking_obj = self.pool.get('stock.picking')        
        move_obj = self.pool.get('stock.move')        
        quant_obj = self.pool.get('stock.quant')        
        
        warehouse_obj = self.pool.get('stock.warehouse')        
        group_obj = self.pool.get('procurement.group')        
        
        values = {}
        data_line = []
        if transfer_id:        
            if not from_warehouse_id:
                raise osv.except_osv(_('Warning'),
                                     _('Please Select Request From .'))          
            transfer_data = transfer_obj.browse(cr, uid, transfer_id, context=context)
            tr_no = transfer_data.name
            warehouse_data = warehouse_obj.browse(cr, uid, from_warehouse_id, context=context)
            group_id = group_obj.search(cr, uid, [('name', '=', tr_no)], context=context) 
            picking_ids = picking_obj.search(cr, uid, [('group_id', '=', group_id),('waybill_no', '!=', None), ('state', 'not in', ('done', 'cancel'))], context=context)             
            for picking_id in picking_ids:     
                picking_data=picking_obj.browse(cr, uid, picking_id, context=context)
                vehicle_no=picking_data.vehicle_no
                waybill_no=picking_data.waybill_no
                move_ids = move_obj.search(cr, uid, [('picking_id', '=', picking_id)], context=context)
                for move_id in move_ids:
                    move_obj.browse(cr, uid, move_id, context=context)
                    quant_ids = quant_obj.search(cr, uid, [('reservation_id', '=', move_id)], context=context)       
                    for line in quant_ids:         
                        order_data = quant_obj.browse(cr, uid, line, context=context)
                        product_id = order_data.product_id.id
                        description = order_data.product_id.product_tmpl_id.description_sale
                        quantity = order_data.qty
                        uom_id = order_data.product_id.uom_id.id
                        sequence = order_data.product_id.product_tmpl_id.sequence
                        uom_ratio = order_data.product_id.uom_ratio
                        storage_location = order_data.location_id.id
                        batch_no = order_data.lot_id.id
                        life_date = order_data.lot_id.life_date
                        data_line.append({
                                              'sequence':sequence,
                                                'product_id':product_id,
                                                 'description': description,
                                                'quantity':quantity,
                                                'uom_id':uom_id,
                                                'uom_ratio':uom_ratio,
                                                'storage_location':storage_location,
                                                'batch_no':batch_no,
                                                'expiry_date':life_date,
                                                'vehicle_no':vehicle_no,
                                                'waybill_no':waybill_no,
                                                  })                
            values = {
                'p_line': data_line,
            }
        return {'value': values}       

    def issue(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'issue' , 'issue_to':uid})        
    
    def taken(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'taken' , 'taken_by':uid})   
    
    def loaded(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'loaded', 'loading_by':uid})      
                       
    def cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'cancel' })    
            
class stock_taking_line(osv.osv):
    _name = 'stock.taking.line'
    _description = 'Taking Line'
    
    def on_change_product_id(self, cr, uid, ids, product_id, context=None):
        values = {}
        res = {'value': {'description': False, 'uom_ratio': False, 'uom_id' :  False, 'sequence':False}}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            cr.execute("""SELECT uom.id FROM product_product pp 
                          LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                          LEFT JOIN product_template_product_uom_rel rel ON (rel.product_template_id=pt.id)
                          LEFT JOIN product_uom uom ON (rel.product_uom_id=uom.id)
                          WHERE pp.id = %s""", (product.id,))
            uom_list = cr.fetchall()
            res['domain'] = {'uom_id': [('id', 'in', uom_list)]}
            res['value'].update({
                    'uom_id': product.product_tmpl_id.uom_id and product.product_tmpl_id.uom_id.id or False,
                    'uom_ratio': product.product_tmpl_id.uom_ratio,
                    'description':product.product_tmpl_id.description_sale,
                    'sequence':product.sequence,
                })

        return res
        

    _columns = {                
        'line_id':fields.many2one('stock.taking', 'Line', ondelete='cascade', select=True),
        'waybill_no':fields.char('WB-Ref;'),
        'product_id': fields.many2one('product.product', 'Item Description', required=True),
        'description':fields.char('Item Specification'),
        'quantity' : fields.float(string='Qty', digits=(16, 0), required=True),
        'uom_id': fields.many2one('product.uom', 'UoM'),
        'uom_ratio':fields.char('Packing Unit'),
         'remark':fields.char('Remark'),
        'sequence':fields.integer('Sequence'),
        'batch_no':fields.many2one('stock.production.lot', 'Batch No'),        
        'expiry_date':fields.date('Expiry'),
        'storage_location':fields.many2one('stock.location', 'Storage Location',required=True),
        'vehicle_no':fields.char('Vehicle No'),

        
        }
        

