'''
Created on Auguest 31, 2016

@author: Administrator
'''
import time

import os
from datetime import datetime,timedelta
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
        sale_order_obj = self.pool.get('sale.order')
        so_line_obj = self.pool.get('stock.requisition').browse(cr, uid, ids, context=context)
        print 'so_line_obj',so_line_obj
        request_date=so_line_obj.request_date
        print 'request_date',request_date
        values = {}
        data_line = []
        order_line = []
        sale_qty=0
        sale_uom=0
        big_req_quantity=0
        req_quantity=0                 
        if sale_team_id:
            sale_team = self.pool.get('crm.case.section').browse(cr, uid, sale_team_id, context=context)
            location = sale_team.location_id
            vehicle_id = sale_team.vehicle_id
            product_line = sale_team.product_ids
            to_location_id=sale_team.issue_location_id
            order_ids = sale_order_obj.search(cr, uid, [('delivery_id', '=', sale_team_id), ('shipped', '=', False),('is_generate','=',False), ('invoiced', '=', False), ('state', 'not in', ['done', 'cancel'])], context=context) 
            print 'order_ids', order_ids
            for line in product_line:                
                product = self.pool.get('product.product').browse(cr, uid, line.id, context=context)                                                  
                data_line.append({
                                    'product_id':line.id,
                                     'product_uom': product.product_tmpl_id.uom_id and product.product_tmpl_id.uom_id.id or False,
                                    'uom_ratio': product.product_tmpl_id.uom_ratio,
                                    'req_quantity':big_req_quantity,
                                    'big_uom_id':product.product_tmpl_id.big_uom_id and product.product_tmpl_id.big_uom_id.id or False,
                                    'big_req_quantity':req_quantity,
                                              })
            for line in order_ids:
                order = sale_order_obj.browse(cr, uid, line, context=context)
                order_line.append({
                                    'name':order.name,
                                     'ref_no':order.tb_ref_no,
                                    'amount':order.amount_total,
                                    'date':order.date_order,
                                    'sale_team_id':order.section_id.id,
                                    'state':order.state,
                                              })              
            values = {
                 'from_location_id':location,
                 'to_location_id':to_location_id ,
                 'vehicle_id':vehicle_id,
                'p_line': data_line,
                'order_line':order_line
            }
        return {'value': values}    
    _columns = {
        'sale_team_id':fields.many2one('crm.case.section', 'Delivery Team', required=True),
        'name': fields.char('(REI)Ref;No.', readonly=True),
        'from_location_id':fields.many2one('stock.location', 'Requested From', required=True),
        'to_location_id':fields.many2one('stock.location', 'Request To'),
        'so_no' : fields.char('Sales Order/Inv Ref;No.'),
        'issue_to':fields.many2one('res.users', "Issue To"),
        'request_by':fields.many2one('res.users', "Requested By"),
        'approve_by':fields.many2one('res.users', "Approved By"),
        'request_date' : fields.datetime('Date Requested'),
         'issue_date':fields.datetime('Date For Issue From'),
         's_issue_date':fields.datetime('Date For Issue To'),
        'vehicle_id':fields.many2one('fleet.vehicle', 'Vehicle No'),
        'state': fields.selection([
            ('draft', 'Request'),
            ('approve', 'Approved'),
            ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
        'p_line':fields.one2many('stock.requisition.line', 'line_id', 'Product Lines',
                              copy=True),
                'company_id':fields.many2one('res.company', 'Company'),
                 'order_line': fields.one2many('stock.requisition.order', 'stock_line_id', 'Sale Order', copy=True),
                 'pre_order':fields.boolean('Pre Order'),
         'partner_id':fields.many2one('res.partner', string='Partner'),

}
    _defaults = {
        'state' : 'draft',
         'company_id': _get_default_company,
         'request_date': fields.datetime.now,
    }     
    
    def create(self, cursor, user, vals, context=None):
        id_code = self.pool.get('ir.sequence').get(cursor, user,
                                                'request.code') or '/'
        vals['name'] = id_code
        return super(stock_requisition, self).create(cursor, user, vals, context=context)

    def so_list(self, cr, uid, ids, context=None):
        sale_order_obj = self.pool.get('sale.order')
        so_line_obj = self.pool.get('stock.requisition.order')
        
        if ids:
            stock_request_data = self.browse(cr, uid, ids[0], context=context)
            issue_date_from = stock_request_data.issue_date
            issue_date_to = stock_request_data.s_issue_date
            sale_team_id = stock_request_data.sale_team_id.id
            request_date=stock_request_data.request_date
            order_ids = sale_order_obj.search(cr, uid, [('delivery_id', '=', sale_team_id), ('shipped', '=', False),('is_generate','=',False), ('invoiced', '=', False), ('state', 'not in', ['done', 'cancel']),('date_order','>',issue_date_from),('date_order','<',issue_date_to)], context=context) 
            print 'order_ids',order_ids,stock_request_data.id
            cr.execute("delete from stock_requisition_order where  stock_line_id=%s",(stock_request_data.id,))
            
            if request_date:
                    cr.execute("select sol.product_id,sum(product_uom_qty) as qty ,sol.product_uom from sale_order so,sale_order_line sol where so.id=sol.order_id and delivery_id=%s and (date_order+ '6 hour'::interval + '30 minutes'::interval)::date between %s and %s group by product_id,product_uom",(sale_team_id,issue_date_from,issue_date_to,))
                    sale_record=cr.fetchall()             
                    print 'sale_record',sale_record      
                    if sale_record:
                        for sale_data in sale_record:
                            product_id=int(sale_data[0])
                            sale_qty=int(sale_data[1])
                            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)                                                                          
                            cr.execute("select floor(1/factor) as ratio from product_uom where active = true and id=%s",(product.product_tmpl_id.big_uom_id.id,))
                            bigger_qty=cr.fetchone()[0]
                            bigger_qty=int(bigger_qty)
                            #print ' bigger_qty',sale_qty,bigger_qty,type(sale_qty),type(bigger_qty)                        
                            big_uom_qty=divmod(sale_qty,bigger_qty)
                            #print 'big_uom_qty',big_uom_qty
                            if  big_uom_qty:
                                big_req_quantity=big_uom_qty[0]
                                req_quantity=big_uom_qty[1]
                                print 'big_req',big_req_quantity,req_quantity
                                cr.execute("update stock_requisition_line set big_req_quantity=%s,req_quantity=%s where product_id=%s and line_id=%s",(big_req_quantity,req_quantity,product_id,stock_request_data.id,))
                                        
            for line in order_ids:
                order = sale_order_obj.browse(cr, uid, line, context=context)                
                so_line_obj.create(cr, uid, {'stock_line_id': stock_request_data.id,
                                                        'name':order.name,
                                                         'ref_no':order.tb_ref_no,
                                                        'amount':order.amount_total,
                                                        'date':order.date_order,
                                                        'sale_team_id':order.section_id.id,
                                                        'state':order.state
                                         }, context=context)        
        return True
    
    def approve(self, cr, uid, ids, context=None):
        product_line_obj = self.pool.get('stock.requisition.line')
        requisition_obj = self.pool.get('stock.requisition')
        sale_order_obj = self.pool.get('sale.order')
        good_obj = self.pool.get('good.issue.note')
        good_line_obj = self.pool.get('good.issue.note.line')
        stock_so_line_obj = self.pool.get('stock.requisition.order')

        req_value = req_lines = {}
        if ids:
            req_value = requisition_obj.browse(cr, uid, ids[0], context=context)
            request_id = req_value.id
            issue_date = req_value.issue_date
            to_location_id = req_value.to_location_id.id
            from_location_id = req_value.from_location_id.id
            vehicle_no = req_value.vehicle_id.id
            sale_team_id = req_value.sale_team_id.id
            for order in req_value.order_line:
                so_name=order.name
                order_id= sale_order_obj.search(cr, uid, [('name', '=', so_name)], context=context) 
                sale_order_obj.write(cr, uid, order_id, {'is_generate':True})    
                print 'order',order_id
            good_id = good_obj.create(cr, uid, {'vehicle_id': vehicle_no,
                                                'sale_team_id':sale_team_id,
                                          'issue_date': issue_date,
                                          'request_id':request_id,
                                          'to_location_id':to_location_id,
                                          'from_location_id':from_location_id}, context=context)
            req_line_id = product_line_obj.search(cr, uid, [('line_id', '=', ids[0])], context=context)
            if good_id and req_line_id:
                
                for id in req_line_id:
                    req_line_value = product_line_obj.browse(cr, uid, id, context=context)
                    if (req_line_value.req_quantity + req_line_value.big_req_quantity) != 0:
                        product_id = req_line_value.product_id.id
                        product_uom = req_line_value.product_uom.id
                        big_uom_id = req_line_value.big_uom_id.id
                        big_req_quantity = req_line_value.big_req_quantity
                        uom_ratio = req_line_value.uom_ratio
                        quantity = req_line_value.req_quantity                        
                        good_line_obj.create(cr, uid, {'line_id': good_id,
                                              'product_id': product_id,
                                              'product_uom': product_uom,
                                              'uom_ratio':uom_ratio,
                                             'big_uom_id':big_uom_id,
                                              'issue_quantity':quantity,
                                              'big_issue_quantity':big_req_quantity}, context=context)
                    
        return self.write(cr, uid, ids, {'state':'approve' ,'request_by':uid})    

            
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
                'big_uom_id': product.product_tmpl_id.big_uom_id and product.product_tmpl_id.big_uom_id.id or False,
            }
        return {'value': values}
        
    _columns = {                
        'line_id':fields.many2one('stock.requisition', 'Line', ondelete='cascade', select=True),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'req_quantity' : fields.float(string='Qty', digits=(16, 0)),
        'product_uom': fields.many2one('product.uom', 'Smaller UOM', required=True),
        'uom_ratio':fields.char('Packing Unit'),
         'remark':fields.char('Remark'),
        'big_uom_id': fields.many2one('product.uom', 'Bigger UOM', required=True, help="Default Unit of Measure used for all stock operation."),
        'big_req_quantity' : fields.float(string='Qty', digits=(16, 0)),
         
    }
        
class stock_requisition_order(osv.osv):  # #prod_pricelist_update_line
    _name = 'stock.requisition.order'
    _description = 'Request OrderLine'
    _columns = {                
        'stock_line_id':fields.many2one('stock.requisition', 'Line', ondelete='cascade', select=True),
        'name': fields.char('Order No'),
        'ref_no' : fields.char('Order Reference'),
        'amount': fields.float('Amount'),
        'date':fields.char('Date'),
        'sale_team_id':fields.many2one('crm.case.section', 'Sales Team'),
        'state': fields.selection([
            ('draft', 'Draft Quotation'),
            ('sent', 'Quotation Sent'),
            ('cancel', 'Cancelled'),
            ('waiting_date', 'Waiting Schedule'),
            ('progress', 'Sales Order'),
            ('manual', 'Sale to Invoice'),
            ('shipping_except', 'Shipping Exception'),
            ('invoice_except', 'Invoice Exception'),
            ('done', 'Done'),
            ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
    }
