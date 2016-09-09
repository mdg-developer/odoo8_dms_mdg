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


class stock_return(osv.osv):
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
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id   
        
    _columns = {
        'name': fields.char('(SRN)Ref;No.', readonly=True),
        'note_id':fields.many2one('good.issue.note', '(GIN)Ref;No.', readonly=True),
        'return_from':fields.many2one('res.users', 'Return From', required=True),
         'so_no' : fields.char('Sales Order/Inv Ref;No.'),
         'return_date':fields.date('Date of Return'),
        'vehicle_id':fields.many2one('fleet.vehicle', 'Vehicle No'),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('confirm', 'Confirmed'),
            ('approve', 'Approved'),
            ('cancel', 'Cancel')
            ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
        'p_line':fields.one2many('stock.return.line', 'line_id', 'Product Lines',
                              copy=True),
                'company_id':fields.many2one('res.company', 'Company'),
}
    _defaults = {
        'state' : 'draft',
         'company_id': _get_default_company,
    }     
    
    def create(self, cursor, user, vals, context=None):
        id_code = self.pool.get('ir.sequence').get(cursor, user,
                                                'stock.return.code') or '/'
        vals['name'] = id_code
        return super(stock_return, self).create(cursor, user, vals, context=context)
    
    def confirm(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'confirm', })
    def cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel', })
    def approve(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'approve'})    

            
class stock_return_line(osv.osv):  # #prod_pricelist_update_line
    _name = 'stock.return.line'
    _description = 'Return Line'

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
        'line_id':fields.many2one('stock.return', 'Line', ondelete='cascade', select=True),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'receive_quantity' : fields.float(string='Received Qty', digits=(16, 0)),
        'return_quantity' : fields.float(string='Returned Qty', digits=(16, 0)),
        'sale_quantity' : fields.float(string='Sales Qty', digits=(16, 0)),
        'foc_quantity' : fields.float(string='FOC Qty', digits=(16, 0)),
        'product_uom': fields.many2one('product.uom', 'UOM', required=True),
        'uom_ratio':fields.char('Packing Unit'),
        'qty_by_wh':fields.char('Received Qty by WH'),
        'expiry_date':fields.char('Expiry'),
         'remark':fields.char('Remark'),
    }
        
   
    
