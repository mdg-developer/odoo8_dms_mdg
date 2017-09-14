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

class stock_transfer_request(osv.osv):
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = "stock.transfer.request"
    _description = "Stock Transfer Request"
    _order = "id desc"    
    _track = {
        'state': {
            'stock_transfer_request.mt_stock_transfer_request_confirm': lambda self, cr, uid, obj, ctx = None: obj.state in ['confirm'],
            'stock_transfer_request.mt_stock_transfer_request_approve': lambda self, cr, uid, obj, ctx = None: obj.state in ['approve']
        },
    }        
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id     
    
    def change_warehouse_id(self, cr, uid, ids, warehouse_id, context=None):
        if warehouse_id:
            warehouse = self.pool.get('stock.warehouse').browse(cr, uid, warehouse_id, context=context)
            return {'value': {'location_id': warehouse.lot_stock_id.id}}
        return {}
    
    _columns = {
        'name': fields.char('TR Ref', readonly=True),
        'warehouse_id':fields.many2one('stock.warehouse', ' Warehouse',required=True),
        'location_id':fields.many2one('stock.location', 'Location',required=True),
        'request_by':fields.many2one('res.users', "Requested By" , readonly=True),
        'approve_by':fields.many2one('res.users', "Approved By", readonly=True),
        'request_date' : fields.date('Date Requested'),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('approve', 'Approved'),
            ('cancel', 'Cancel'),
            ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
        'p_line':fields.one2many('stock.transfer.request.line', 'line_id', 'Product Lines',
                              copy=True),
    'company_id':fields.many2one('res.company', 'Company'),
     'partner_id':fields.many2one('res.partner', string='Partner'),

}
    _defaults = {
        'state' : 'draft',
         'company_id': _get_default_company,
         'request_date': fields.datetime.now,
         'request_by':lambda obj, cr, uid, context: uid
    }     
    
    def create(self, cursor, user, vals, context=None):
        id_code = self.pool.get('ir.sequence').get(cursor, user,
                                                'stock.transfer.request.code') or '/'
        vals['name'] = id_code
        return super(stock_transfer_request, self).create(cursor, user, vals, context=context)
   
    def approve(self, cr, uid, ids, context=None):
        transfer_data=self.browse(cr, uid, ids[0], context=context)
        transfer_line_obj = self.pool.get("stock.transfer.request.line")
        proc_obj = self.pool.get("procurement.order")
        new_group = self.pool.get("procurement.group").create(cr, uid, {'name': transfer_data.name}, context=context)

        for  line_data in transfer_data.p_line:
                line=transfer_line_obj.browse(cr, uid,line_data.id, context=context)

                vals = {
                    'name': line.description,
                    'warehouse_id':transfer_data.warehouse_id.id,
                    'location_id':transfer_data.location_id.id,
                    'origin':transfer_data.name,
                    'company_id': transfer_data.company_id.id,
                    'date_planned': transfer_data.request_date,
                    'product_id': line.product_id.id,
                    'product_qty': line.quantity,
                    'product_uom': line.uom_id.id,
                    'product_uos_qty': line.uom_id.id,
                    'product_uos': line.uom_id.id,
                    'group_id':new_group,
                    }
                proc = proc_obj.create(cr, uid, vals, context=context)
              #  proc_obj.run(cr, uid, [proc], context=context)
        cr.execute("update stock_picking set is_transfer_request =True where group_id =%s",(new_group,))
        return self.write(cr, uid, ids, {'state':'approve' , 'approve_by':uid})    
    
    def cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'cancel' })    
            
class stock_transfer_request_line(osv.osv):
    _name = 'stock.transfer.request.line'
    _description = 'Request Line'
    
    
    def on_change_product_id(self, cr, uid, ids, product_id, context=None):
        values = {}
        res = {'value': {'description': False, 'uom_ratio': False, 'uom_id' :  False,'sequence':False}}
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
        'line_id':fields.many2one('stock.transfer.request', 'Line', ondelete='cascade', select=True),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'description':fields.char('Item Specification', required=True),
        'quantity' : fields.float(string='Qty', digits=(16, 0), required=True),
        'uom_id': fields.many2one('product.uom', 'UOM'),
        'uom_ratio':fields.char('Packing Unit'),
         'remark':fields.char('Remark'),
        'sequence':fields.integer('Sequence'),
    }
        

