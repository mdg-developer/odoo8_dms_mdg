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

class way_bill(osv.osv):
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = "way.bill"
    _description = "Way Bill"
    _order = "id desc"    
    _track = {
        'state': {
            'way_bill.mt_way_bill_confirm': lambda self, cr, uid, obj, ctx = None: obj.state in ['confirm'],
            'way_bill.mt_way_bill_approve': lambda self, cr, uid, obj, ctx = None: obj.state in ['approve']
        },
    }        
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id     
    
    _columns = {
        'name': fields.char('WB Ref', readonly=True),
        'transfer_id':fields.many2one('stock.transfer.request', ' TR.Ref No', required=True),
        'from_warehouse_id':fields.many2one('stock.warehouse', 'Dispatched From', required=True),
        'to_warehouse_id':fields.many2one('stock.warehouse', 'Dispatched To', required=True),
        'received_by':fields.many2one('res.users', "Received By" , readonly=True),
        'checked_by':fields.many2one('res.users', "Checked By", readonly=True),
        'loading_by': fields.char('Loading By'),
        'transported_by': fields.char('Transported By'),
        'transport_type': fields.char('Transport Type'),
        'approved_by': fields.char('Approved By'),
        'transport_mode': fields.char('Transport Mode'),
        'vehicle_no': fields.char('Vehicle No'),
        'consignee': fields.char('Consignee'),
        'loading_date' : fields.datetime('Loading Date & Time'),
        'departure_date' : fields.datetime('Departure Date & Time'),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('received', 'Received'),
            ('checked', 'Checked'),
            ('cancel', 'Cancel'),
            ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
        'p_line':fields.one2many('way.bill.line', 'line_id', 'Product Lines',
                              copy=True),
    'company_id':fields.many2one('res.company', 'Company'),
     'partner_id':fields.many2one('res.partner', string='Partner'),

}
    _defaults = {
        'state' : 'draft',
         'company_id': _get_default_company,
         'date': fields.datetime.now,
    }     
    
    def create(self, cursor, user, vals, context=None):
        id_code = self.pool.get('ir.sequence').get(cursor, user,
                                                'way.bill.code') or '/'
        vals['name'] = id_code
        return super(way_bill, self).create(cursor, user, vals, context=context)
    
    def on_change_transfer_id(self, cr, uid, ids, transfer_id, context=None):
        procurement_order_obj = self.pool.get('procurement.order')      
        transfer_obj = self.pool.get('stock.transfer.request')      
        picking_obj = self.pool.get('stock.picking')        
        move_obj = self.pool.get('stock.move')        
        values = {}
        data_line = []
        if transfer_id:        
            transfer_data = transfer_obj.browse(cr, uid, transfer_id, context=context)
            tr_no = transfer_data.name
            order_ids = procurement_order_obj.search(cr, uid, [('origin', '=', tr_no)], context=context) 
            for line in order_ids:          
                order_data = procurement_order_obj.browse(cr, uid, line, context=context)
                to_warehouse = order_data.warehouse_id.id
                product_id = order_data.product_id.id
                description = order_data.product_id.product_tmpl_id.description_sale
                quantity = order_data.product_qty
                uom_id = order_data.product_uom.id
                sequence = order_data.product_id.product_tmpl_id.sequence
                uom_ratio = order_data.product_id.uom_ratio
                
                data_line.append({
                                      'sequence':sequence,
                                        'product_id':product_id,
                                         'description': description,
                                        'quantity':quantity,
                                        'uom_id':uom_id,
                                        'uom_ratio':uom_ratio,
                                          })                
            values = {
                'to_warehouse_id':to_warehouse,
                'p_line': data_line,
            }
        return {'value': values}       

    def receive(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'received' ,'received_by':uid})        
    def check(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'checked' ,'checked_by':uid})            
    def cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'cancel' })    
            
class way_bill_line(osv.osv):
    _name = 'way.bill.line'
    _description = 'Bill Line'
    
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
        'line_id':fields.many2one('way.bill', 'Line', ondelete='cascade', select=True),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'description':fields.char('Item Specification', required=True),
        'quantity' : fields.float(string='Qty', digits=(16, 0), required=True),
        'uom_id': fields.many2one('product.uom', 'UOM'),
        'uom_ratio':fields.char('Packing Unit'),
         'remark':fields.char('Remark'),
        'sequence':fields.integer('Sequence'),
                'batch_no':fields.many2one('stock.production.lot', 'Batch No'),
                'expiry_date':fields.date('Expiry'),
        }
        

