'''
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

class issue_requisition(osv.osv):
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = "issue.requisition"
    _description = "Issue Requisition"
    _order = "id desc"    
    _track = {
        'state': {
            'issue_requisition.mt_requisition_confirm': lambda self, cr, uid, obj, ctx = None: obj.state in ['confirm'],
            'issue_requisition.mt_requisition_approve': lambda self, cr, uid, obj, ctx = None: obj.state in ['approve']
        },
    }       
    
    _columns = {
        'name': fields.char('(TR) Ref:No.', readonly=True),
        'request_id':fields.many2one('stock.requisition', '(RFI) Ref:No.', readonly=True),
        'request_from':fields.many2one('res.users', 'Request From'),
        'to_location_id':fields.many2one('stock.location', 'Request To'),
        'so_no' : fields.char('Reference of Sales Request'),
        'issue_for':fields.many2one('stock.location', "Issue For"),
        'request_date' : fields.datetime('Date Requested'),
         'issue_date':fields.datetime('Date For Issue'),
        'state': fields.selection([
            ('draft', 'Pending'),
            ('approve', 'Approved'),
            ('cancel', 'Cancel')
            ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
        'p_line':fields.one2many('issue.requisition.line', 'line_id', 'Product Lines',
                              copy=True),
        'vehicle_id':fields.many2one('fleet.vehicle', 'Vehicle No'),
        

}
    _defaults = {
        'state' : 'draft',
        'request_date':datetime.datetime.now(),

    }     
    
    def create(self, cursor, user, vals, context=None):
        id_code = self.pool.get('ir.sequence').get(cursor, user,
                                                'issue_request.code') or '/'
        vals['name'] = id_code
        return super(issue_requisition, self).create(cursor, user, vals, context=context)

    def cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel', })
    
    def approve(self, cr, uid, ids, context=None):
        product_line_obj = self.pool.get('issue.requisition.line')
        requisition_obj = self.pool.get('issue.requisition')
        good_obj = self.pool.get('good.issue.note')
        good_line_obj = self.pool.get('good.issue.note.line')

        req_value = req_lines = {}
        if ids:
            req_value = requisition_obj.browse(cr, uid, ids[0], context=context)
            if req_value.state=='approve':
                raise osv.except_osv(_('Warning'),
                                         _('You cannot transfer a record in Approved state'))                  
            request_id = req_value.id
            issue_date = req_value.issue_date
            to_location_id = req_value.to_location_id.id
            from_location_id = req_value.from_location_id.id
            good_id = good_obj.create(cr, uid, {'issue_date': issue_date,
                                          'request_id':request_id,
                                          'to_location_id':to_location_id,
                                          'from_location_id':from_location_id}, context=context)
            req_line_id = product_line_obj.search(cr, uid, [('line_id', '=', ids[0])], context=context)
            if good_id and req_line_id:
                
                for id in req_line_id:
                    req_line_value = product_line_obj.browse(cr, uid, id, context=context)
                    if req_line_value.req_quantity!=0:
                        product_id = req_line_value.product_id.id
                        product_uom = req_line_value.product_uom.id
                        uom_ratio = req_line_value.uom_ratio
                        quantity = req_line_value.req_quantity
                        good_line_obj.create(cr, uid, {'line_id': good_id,
                                              'product_id': product_id,
                                              'product_uom': product_uom,
                                              'uom_ratio':uom_ratio,
                                              'approved_quantity':quantity,
                                              'issue_quantity':quantity}, context=context)
                    
        return self.write(cr, uid, ids, {'state':'approve'})    

            
class issue_requisition_line(osv.osv):  # #prod_pricelist_update_line
    _name = 'issue.requisition.line'
    _description = 'Request Line'

    def on_change_product_id(self, cr, uid, ids, product_id, context=None):
        values = {}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            values = {
                'product_uom': product.product_tmpl_id.uom_id and product.product_tmpl_id.uom_id.id or False,
                'uom_ratio': product.product_tmpl_id.uom_ratio,
                'big_uom_id': product.product_tmpl_id.big_uom_id and product.product_tmpl_id.big_uom_id.id or False,
            }
        return {'value': values}
    
    _columns = {                
        'line_id':fields.many2one('issue.requisition', 'Line', ondelete='cascade', select=True),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'req_quantity' : fields.float(string='Qty', digits=(16, 0)),
        #'product_uom': fields.many2one('product.uom', 'UOM', required=True),
        'product_uom': fields.many2one('product.uom', 'Smaller UOM',readonly=True),
        'uom_ratio':fields.char('Packing Unit'),
        'remark':fields.char('Remark'),
        'big_uom_id': fields.many2one('product.uom', 'Bigger UOM',  help="Default Unit of Measure used for all stock operation.",readonly=True),
        'big_req_quantity' : fields.float(string='Qty', digits=(16, 0)),
    }
        
   
    
