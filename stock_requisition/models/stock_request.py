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

class stock_requisition(osv.osv):
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = "stock.requisition"
    _description = "Stock Requisition"
    _order = "id desc"    
    _track = {
        'state': {
            'stock_requisition.mt_requisition_confirm': lambda self, cr, uid, obj, ctx = None: obj.state in ['confirm'],
            'stock_requisition.mt_requisition_approve': lambda self, cr, uid, obj, ctx = None: obj.state in ['approve']
        },
    }    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id     
    
    def on_change_sale_team_id(self, cr, uid, ids, sale_team_id, context=None):
        values = {}
        data_line = []
        if sale_team_id:
            sale_team = self.pool.get('crm.case.section').browse(cr, uid, sale_team_id, context=context)
            location = sale_team.location_id
            vehicle_id=sale_team.vehicle_id
            product_line = sale_team.product_ids
            for line in product_line:
                product = self.pool.get('product.product').browse(cr, uid, line.id, context=context)
                data_line.append({
                                    'product_id':line.id,
                                     'product_uom': product.product_tmpl_id.uom_id and product.product_tmpl_id.uom_id.id or False,
                                    'uom_ratio': product.product_tmpl_id.uom_ratio,
                                    'req_quantity':0.0,
                                              })
            values = {
                 'from_location_id':location,
                 'vehicle_id':vehicle_id,
                'p_line': data_line,
            }
        return {'value': values}    
    _columns = {
        'sale_team_id':fields.many2one('crm.case.section', 'Sale Team'),
        'name': fields.char('(REI)Ref;No.', readonly=True),
        'from_location_id':fields.many2one('stock.location', 'Request From'),
        'to_location_id':fields.many2one('stock.location', 'Request To'),
        'so_no' : fields.char('Sales Order/Inv Ref;No.'),
        'issue_to':fields.many2one('res.users', "Issue To"),
        'request_by':fields.many2one('res.users', "Request By"),
        'approve_by':fields.many2one('res.users', "Approve By"),
        'request_date' : fields.datetime('Date Requested'),
         'issue_date':fields.datetime('Date For Issue'),
        'vehicle_id':fields.many2one('fleet.vehicle', 'Vehicle No'),
        'state': fields.selection([
            ('draft', 'Pending'),
            ('approve', 'Approved'),
            ('cancel', 'Cancel')
            ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
        'p_line':fields.one2many('stock.requisition.line', 'line_id', 'Product Lines',
                              copy=True),
                'company_id':fields.many2one('res.company', 'Company'),

}
    _defaults = {
        'state' : 'draft',
         'company_id': _get_default_company,
         'request_date':datetime.datetime.now(),

    }     
    
    def create(self, cursor, user, vals, context=None):
        id_code = self.pool.get('ir.sequence').get(cursor, user,
                                                'request.code') or '/'
        vals['name'] = id_code
        return super(stock_requisition, self).create(cursor, user, vals, context=context)

    def cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel', })
    
    def approve(self, cr, uid, ids, context=None):
        product_line_obj = self.pool.get('stock.requisition.line')
        requisition_obj = self.pool.get('stock.requisition')
        good_obj = self.pool.get('good.issue.note')
        good_line_obj = self.pool.get('good.issue.note.line')

        req_value = req_lines = {}
        if ids:
            req_value = requisition_obj.browse(cr, uid, ids[0], context=context)
            request_id = req_value.id

            issue_date = req_value.issue_date
            to_location_id = req_value.to_location_id.id
            from_location_id = req_value.from_location_id.id
            vehicle_no = req_value.vehicle_id.id
            good_id = good_obj.create(cr, uid, {'vehicle_id': vehicle_no,
                                          'issue_date': issue_date,
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
                                              'issue_quantity':quantity}, context=context)
                    
        return self.write(cr, uid, ids, {'state':'approve'})    

            
class stock_requisition_line(osv.osv):  # #prod_pricelist_update_line
    _name = 'stock.requisition.line'
    _description = 'Request Line'

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
        'line_id':fields.many2one('stock.requisition', 'Line', ondelete='cascade', select=True),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'req_quantity' : fields.float(string='Qty', digits=(16, 0)),
        'product_uom': fields.many2one('product.uom', 'UOM', required=True),
                'uom_ratio':fields.char('Packing Unit'),
                'remark':fields.char('Remark'),
    }
        
   
    
