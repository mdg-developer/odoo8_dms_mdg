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
    
    def on_change_sale_team_id(self, cr, uid, ids, sale_team_id, pre_order, context=None):
        sale_order_obj = self.pool.get('sale.order')
        so_line_obj = self.pool.get('stock.requisition').browse(cr, uid, ids, context=context)
        print 'so_line_obj', so_line_obj
        request_date = so_line_obj.request_date
        print 'request_date', request_date
        values = {}
        data_line = []
        order_line = []
        big_req_quantity = 0
        req_quantity = 0   
        sale_req_quantity = 0
        addtional_req_quantity = 0
        if sale_team_id:
            sale_team = self.pool.get('crm.case.section').browse(cr, uid, sale_team_id, context=context)
            issue_to = sale_team.receiver
            location = sale_team.location_id
            vehicle_id = sale_team.vehicle_id
            product_line = sale_team.product_ids
            to_location_id = sale_team.issue_location_id
            order_ids = sale_order_obj.search(cr, uid, [('delivery_id', '=', sale_team_id), ('shipped', '=', False), ('is_generate', '=', False), ('invoiced', '=', False), ('state', 'not in', ['done', 'cancel'])], context=context) 
            for line in product_line:                
                product = self.pool.get('product.product').browse(cr, uid, line.id, context=context)   
                cr.execute('select  SUM(COALESCE(qty,0)) qty from stock_quant where location_id=%s and product_id=%s and qty >0 group by product_id', (to_location_id.id, product.id,))
                qty_on_hand = cr.fetchone()
                if qty_on_hand:
                    qty_on_hand = qty_on_hand[0]
                else:
                    qty_on_hand = 0
                if product.product_tmpl_id.type=='product':                                               
                    data_line.append({
                                      'sequence':product.sequence,
                                        'product_id':line.id,
                                         'product_uom': product.product_tmpl_id.uom_id and product.product_tmpl_id.uom_id.id or False,
                                        'uom_ratio': product.product_tmpl_id.uom_ratio,
                                        'req_quantity':big_req_quantity,
                                        'big_uom_id':product.product_tmpl_id.big_uom_id and product.product_tmpl_id.big_uom_id.id or False,
                                        'big_req_quantity':req_quantity,
                                        'sale_req_quantity':sale_req_quantity,
                                        'addtional_req_quantity':addtional_req_quantity,
                                        'qty_on_hand':qty_on_hand,
                                          })
            for line in order_ids:
                order = sale_order_obj.browse(cr, uid, line, context=context)
                date_order = order.date_order    
                cr.execute("select (date_order+ '6 hour'::interval + '30 minutes'::interval)  from sale_order where id=%s", (order.id,))
                sale_date = cr.fetchone()[0]
                order_line.append({
                                    'name':order.name,
                                     'ref_no':order.tb_ref_no,
                                    'amount':order.amount_total,
                                    'date':sale_date,
                                    'sale_team_id':order.section_id.id,
                                    'state':order.state,
                                              }) 
            values = {
                 'from_location_id':location,
                 'to_location_id':to_location_id ,
                 'vehicle_id':vehicle_id,
                'p_line': data_line,
                'order_line':order_line,
                'issue_to':issue_to,
            }
        return {'value': values}    
    _columns = {
        'sale_team_id':fields.many2one('crm.case.section', 'Delivery Team', required=True),
        'name': fields.char('RFI Ref', readonly=True),
        'from_location_id':fields.many2one('stock.location', 'Requesting  Location', required=True),
        'to_location_id':fields.many2one('stock.location', 'Request Warehouse'),
        'so_no' : fields.char('Sales Order/Inv Ref;No.'),
        'issue_to':fields.char("Receiver"),
        'request_by':fields.many2one('res.users', "Requested By" , readonly=True),
        'approve_by':fields.many2one('res.users', "Approved By", readonly=True),
        'request_date' : fields.date('Date Requested'),
         'issue_date':fields.date('Order Date From', required=True),
         's_issue_date':fields.date('Order Date To', required=True),
        'vehicle_id':fields.many2one('fleet.vehicle', 'Vehicle No'),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('approve', 'Approved'),
            ('cancel', 'Cancel'),
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
    'good_issue_id':fields.many2one('good.issue.note', 'GIN No' ,readonly=True),

}
    _defaults = {
        'state' : 'draft',
         'company_id': _get_default_company,
         'request_date': fields.datetime.now,
         'issue_date':fields.datetime.now,
         's_issue_date':fields.datetime.now,
         'request_by':lambda obj, cr, uid, context: uid
         
    }     
    
    def create(self, cursor, user, vals, context=None):
        if vals['sale_team_id']:
            sale_team_id=vals['sale_team_id']
            sale_team = self.pool.get('crm.case.section').browse(cursor, user, sale_team_id, context=context)
            to_location_id = sale_team.issue_location_id.id            
            from_location_id=sale_team.location_id.id
        id_code = self.pool.get('ir.sequence').get(cursor, user,
                                                'request.code') or '/'
        vals['name'] = id_code
        vals['to_location_id'] = to_location_id
        vals['from_location_id'] = from_location_id
        return super(stock_requisition, self).create(cursor, user, vals, context=context)

    def so_list(self, cr, uid, ids, context=None):
        try:
            sale_order_obj = self.pool.get('sale.order')
            so_line_obj = self.pool.get('stock.requisition.order')
            if ids:
                stock_request_data = self.browse(cr, uid, ids[0], context=context)
                issue_date_from = stock_request_data.issue_date
                issue_date_to = stock_request_data.s_issue_date
                sale_team_id = stock_request_data.sale_team_id.id
                request_date = stock_request_data.request_date
                location_id = stock_request_data.to_location_id.id
                
                #sql = 'select id from sale_order where delivery_id=%s, shipped=False and is_generate=False and invoiced=False and state not in (%s,%s) and date_order between %s and %s'
                #cr.execute(sql,(sale_team_id,issue_date_from,issue_date_to))
                #order_ids = cr.fetchall()
                #order_ids= []
                print 'issue_date_from',issue_date_from,issue_date_to
                if issue_date_from == issue_date_to:
                    order_ids = sale_order_obj.search(cr, uid, [('delivery_id', '=', sale_team_id), ('shipped', '=', False), ('is_generate', '=', False), ('invoiced', '=', False), ('state', 'not in', ['done', 'cancel']), ('date_order', '<=', issue_date_from), ('date_order', '<=', issue_date_to)], context=context) 
                else:
                    order_ids = sale_order_obj.search(cr, uid, [('delivery_id', '=', sale_team_id), ('shipped', '=', False), ('is_generate', '=', False), ('invoiced', '=', False), ('state', 'not in', ['done', 'cancel']), ('date_order', '>=', issue_date_from), ('date_order', '<=', issue_date_to)], context=context) 
                print 'order_idsorder_ids',order_ids
                cr.execute("delete from stock_requisition_order where  stock_line_id=%s", (stock_request_data.id,))
                cr.execute("update stock_requisition_line set sale_req_quantity=0 where line_id=%s", (stock_request_data.id,))
                order_list = str(tuple(order_ids))
                order_list = eval(order_list)
                if request_date and order_list:
                        cr.execute("select sol.product_id,sum(product_uom_qty) as qty ,sol.product_uom from sale_order so,sale_order_line sol where so.id=sol.order_id and so.id in %s group by product_id,product_uom", (order_list,))
                        sale_record = cr.fetchall()             
                        if sale_record:
                            for sale_data in sale_record:
                                product_id = int(sale_data[0])
                                sale_qty = int(sale_data[1])
                                sale_product_uom = int(sale_data[2])
                                product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
                                sequence=product.sequence
                                cr.execute('select  SUM(COALESCE(qty,0)) qty from stock_quant where location_id=%s and product_id=%s and qty >0 group by product_id', (location_id, product_id,))
                                qty_on_hand = cr.fetchone()
                                if qty_on_hand:
                                    qty_on_hand = qty_on_hand[0]
                                else:
                                    qty_on_hand = 0
                                if sale_product_uom == product.product_tmpl_id.big_uom_id.id:                                                                          
                                    cr.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (product.product_tmpl_id.big_uom_id.id,))
                                    bigger_qty = cr.fetchone()[0]
                                    bigger_qty = int(bigger_qty)
                                    sale_qty = bigger_qty * sale_qty
                                cr.execute("update stock_requisition_line set sale_req_quantity=sale_req_quantity+%s,qty_on_hand=%s,sequence=%s where product_id=%s and line_id=%s", (sale_qty, qty_on_hand, sequence,product_id, stock_request_data.id,))
                                            
                for line in order_ids:
                    order = sale_order_obj.browse(cr, uid, line, context=context)                
                    cr.execute("select (date_order+ '6 hour'::interval + '30 minutes'::interval)  from sale_order where id=%s", (order.id,))
                    sale_date = cr.fetchone()[0]                
                    so_line_obj.create(cr, uid, {'stock_line_id': stock_request_data.id,
                                                            'name':order.name,
                                                             'ref_no':order.tb_ref_no,
                                                            'amount':order.amount_total,
                                                            'date':sale_date,
                                                            'sale_team_id':order.section_id.id,
                                                            'state':order.state
                                             }, context=context) 
        except ValueError as err: 
            message = 'Unable to refresh sale order %s', err   
            #raise message 
        return True
    
    def updateQtyOnHand(self, cr, uid, ids, context=None):
        product_line_obj = self.pool.get('stock.requisition.line')
        if ids:
            stock_request_data = self.browse(cr, uid, ids[0], context=context)
            location_id = stock_request_data.to_location_id.id
            req_line_id = product_line_obj.search(cr, uid, [('line_id', '=', ids[0])], context=context)
            for data in req_line_id:
                req_line_value = product_line_obj.browse(cr, uid, data, context=context)
                line_id= req_line_value.id
                product_id = req_line_value.product_id.id
                cr.execute('select  SUM(COALESCE(qty,0)) qty from stock_quant where location_id=%s and product_id=%s and qty >0 group by product_id', (location_id, product_id,))
                qty_on_hand = cr.fetchone()
                if qty_on_hand:
                    qty_on_hand = qty_on_hand[0]
                else:
                    qty_on_hand = 0
                cr.execute("update stock_requisition_line set qty_on_hand=%s where product_id=%s and id=%s", (qty_on_hand, product_id,line_id,))
                
    def approve(self, cr, uid, ids, context=None):
         
        transfer_line_obj = self.pool.get("stock.transfer.request.line")
        product_line_obj = self.pool.get('stock.requisition.line')
        requisition_obj = self.pool.get('stock.requisition')
        stock_warehouse_obj = self.pool.get('stock.warehouse')
        proc_obj = self.pool.get("procurement.order")
        
        if ids:
            req_value = requisition_obj.browse(cr, uid, ids[0], context=context)
        new_group = self.pool.get("procurement.group").create(cr, uid, {'name': req_value.name}, context=context)
        
            
        #for  line_data in transfer_data.p_line:
        for line in req_value.p_line:
             
            warehouse_id = stock_warehouse_obj.search(cr,uid,[('lot_stock_id','=',req_value.from_location_id.id)])
            vals = {
                    'name': line.product_id.name_template,
                    'warehouse_id':warehouse_id[0],
                    'location_id':req_value.from_location_id.id,
                    'origin':req_value.name,
                    'company_id': line.line_id.company_id.id,
                    'date_planned': line.line_id.request_date,
                    'product_id': line.product_id.id,
                    'product_qty': line.product_quantity,
                    'product_uom': line.product_uos.id,
                    'product_uos_qty':line.product_quantity,
                    'product_uos': line.product_uos.id,
                    'group_id':new_group,
                    }
            proc = proc_obj.create(cr, uid, vals, context=context)
            
        return self.write(cr, uid, ids, {'state':'approve' , 'approve_by':uid})    
#         
#         
#         product_line_obj = self.pool.get('stock.requisition.line')
#         requisition_obj = self.pool.get('stock.requisition')
#         sale_order_obj = self.pool.get('sale.order')
#         good_obj = self.pool.get('good.issue.note')
#         good_line_obj = self.pool.get('good.issue.note.line')
#         procurement_order_obj = self.pool.get('procurement.order')
#         procurement_rule_obj = self.pool.get('procurement.rule')
#         req_value = {}
#         if ids:
#             req_value = requisition_obj.browse(cr, uid, ids[0], context=context)
#             request_id = req_value.id
#             request_date = req_value.request_date
#             request_by = req_value.request_by.id
#             to_location_id = req_value.to_location_id.id
#             from_location_id = req_value.from_location_id.id
#             ref_no = req_value.name
#             #vehicle_no = req_value.vehicle_id.id
#             sale_team_id = req_value.sale_team_id.id
#             branch_id = req_value.branch_id.id
#             receiver = req_value.sale_team_id.receiver
#             rule_id = procurement_rule_obj.search(cr,uid,[('location_id', '=', to_location_id)],context=context)
#             if rule_id:
#                 rule_data = procurement_rule_obj.browse(cr,uid,rule_id,context=context)
#             for line in req_value.p_line:
#                 value = {
#                          'orgin':ref_no,
#                          'product_id': line.product_id.id,
#                          'product_qty': line.product_qty,
#                          'product_uom' : line.product_uom.id,
#                          'company_id' : line.line_id.company_id.id,
#                          'rule_id': rule_id,
#                          'date_planned': line.requested_date
#                          }
#                 procument_id = procurement_order_obj.create(cr,uid,value,context=context)


#             for order in req_value.order_line:
#                 so_name = order.name
#                 order_id = sale_order_obj.search(cr, uid, [('name', '=', so_name)], context=context) 
#                 sale_order_obj.write(cr, uid, order_id, {'is_generate':True})    
#             good_id = good_obj.create(cr, uid, {
#                                           'sale_team_id':sale_team_id,
#                                           'issue_date': request_date,
#                                           'request_id':request_id,
#                                           'request_by':request_by,
#                                           'to_location_id':to_location_id,
#                                           'from_location_id':from_location_id,
#                                           'receiver':receiver,
#                                           'branch_id':branch_id}, context=context)
#             
#             req_line_id = product_line_obj.search(cr, uid, [('line_id', '=', ids[0])], context=context)
#             if good_id and req_line_id:
#                 cr.execute('select sum(req_quantity+big_req_quantity) from stock_requisition_line where line_id=%s ', (ids[0],))
#                 condition_data = cr.fetchone()[0]         
#                 if condition_data == 0.0:
#                     raise osv.except_osv(_('Warning'),
#                                      _('Please Press Update Qty Button'))                
#                 for data in req_line_id:
#                     req_line_value = product_line_obj.browse(cr, uid, data, context=context)
#                     if (req_line_value.req_quantity + req_line_value.big_req_quantity) != 0:
#                         product_id = req_line_value.product_id.id
#                         product_uom = req_line_value.product_uom.id
#                         qty_on_hand = req_line_value.qty_on_hand
#                         big_uom_id = req_line_value.big_uom_id.id
#                         big_req_quantity = req_line_value.big_req_quantity
#                         uom_ratio = req_line_value.uom_ratio
#                         quantity = req_line_value.req_quantity
#                         sequence=req_line_value.sequence
#                         product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)                                                                          
#                         cr.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (product.product_tmpl_id.big_uom_id.id,))
#                         bigger_qty = cr.fetchone()[0]
#                         bigger_qty = int(bigger_qty)
#                         if  bigger_qty:
#                             small_qty = big_req_quantity * bigger_qty
#                             ori_small_qty = quantity
#                             total = small_qty + ori_small_qty
#                         if total > qty_on_hand:
#                             raise osv.except_osv(_('Warning'),
#                                      _('Please Check Qty On Hand For (%s)') % (product.name_template,))
#                         else:          
#                             good_line_obj.create(cr, uid, {'line_id': good_id,
#                                                   'product_id': product_id,
#                                                   'product_uom': product_uom,
#                                                   'uom_ratio':uom_ratio,
#                                                  'big_uom_id':big_uom_id,
#                                                   'issue_quantity':quantity,
#                                                   'big_issue_quantity':big_req_quantity,
#                                                   'qty_on_hand':qty_on_hand,
#                                                   'sequence':sequence,
#                                                   }, context=context)
#         return self.write(cr, uid, ids, {'state':'approve' , 'approve_by':uid,'good_issue_id':good_id})    
#     def approve(self, cr, uid, ids, context=None):
#         product_line_obj = self.pool.get('stock.requisition.line')
#         requisition_obj = self.pool.get('stock.requisition')
#         sale_order_obj = self.pool.get('sale.order')
#         good_obj = self.pool.get('good.issue.note')
#         good_line_obj = self.pool.get('good.issue.note.line')
#         req_value = {}
#         if ids:
#             req_value = requisition_obj.browse(cr, uid, ids[0], context=context)
#             request_id = req_value.id
#             request_date = req_value.request_date
#             request_by = req_value.request_by.id
#             to_location_id = req_value.to_location_id.id
#             from_location_id = req_value.from_location_id.id
#             #vehicle_no = req_value.vehicle_id.id
#             sale_team_id = req_value.sale_team_id.id
#             branch_id = req_value.branch_id.id
#             receiver = req_value.sale_team_id.receiver
#             for order in req_value.order_line:
#                 so_name = order.name
#                 order_id = sale_order_obj.search(cr, uid, [('name', '=', so_name)], context=context) 
#                 sale_order_obj.write(cr, uid, order_id, {'is_generate':True})    
#             good_id = good_obj.create(cr, uid, {
#                                           'sale_team_id':sale_team_id,
#                                           'issue_date': request_date,
#                                           'request_id':request_id,
#                                           'request_by':request_by,
#                                           'to_location_id':to_location_id,
#                                           'from_location_id':from_location_id,
#                                           'receiver':receiver,
#                                           'branch_id':branch_id}, context=context)
#             
#             req_line_id = product_line_obj.search(cr, uid, [('line_id', '=', ids[0])], context=context)
#             if good_id and req_line_id:
#                 cr.execute('select sum(req_quantity+big_req_quantity) from stock_requisition_line where line_id=%s ', (ids[0],))
#                 condition_data = cr.fetchone()[0]         
#                 if condition_data == 0.0:
#                     raise osv.except_osv(_('Warning'),
#                                      _('Please Press Update Qty Button'))                
#                 for data in req_line_id:
#                     req_line_value = product_line_obj.browse(cr, uid, data, context=context)
#                     if (req_line_value.req_quantity + req_line_value.big_req_quantity) != 0:
#                         product_id = req_line_value.product_id.id
#                         product_uom = req_line_value.product_uom.id
#                         qty_on_hand = req_line_value.qty_on_hand
#                         big_uom_id = req_line_value.big_uom_id.id
#                         big_req_quantity = req_line_value.big_req_quantity
#                         uom_ratio = req_line_value.uom_ratio
#                         quantity = req_line_value.req_quantity
#                         sequence=req_line_value.sequence
#                         product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)                                                                          
#                         cr.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (product.product_tmpl_id.big_uom_id.id,))
#                         bigger_qty = cr.fetchone()[0]
#                         bigger_qty = int(bigger_qty)
#                         if  bigger_qty:
#                             small_qty = big_req_quantity * bigger_qty
#                             ori_small_qty = quantity
#                             total = small_qty + ori_small_qty
#                         if total > qty_on_hand:
#                             raise osv.except_osv(_('Warning'),
#                                      _('Please Check Qty On Hand For (%s)') % (product.name_template,))
#                         else:          
#                             good_line_obj.create(cr, uid, {'line_id': good_id,
#                                                   'product_id': product_id,
#                                                   'product_uom': product_uom,
#                                                   'uom_ratio':uom_ratio,
#                                                  'big_uom_id':big_uom_id,
#                                                   'issue_quantity':quantity,
#                                                   'big_issue_quantity':big_req_quantity,
#                                                   'qty_on_hand':qty_on_hand,
#                                                   'sequence':sequence,
#                                                   }, context=context)
#         return self.write(cr, uid, ids, {'state':'approve' , 'approve_by':uid,'good_issue_id':good_id})    
    
    def cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'cancel' })    

    def update_data(self, cr, uid, ids, context=None):
        product_line_obj = self.pool.get('stock.requisition.line')
        req_line_id = product_line_obj.search(cr, uid, [('line_id', '=', ids[0])], context=context)
        for data in req_line_id:
            req_line_value = product_line_obj.browse(cr, uid, data, context=context)
            sale_req_qty = req_line_value.sale_req_quantity
            add_req_qty = req_line_value.addtional_req_quantity
            product_id = req_line_value.product_id.id
            print 'product_id',product_id
            total_qty = sale_req_qty + add_req_qty
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)                                                                          
            cr.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (product.product_tmpl_id.big_uom_id.id,))
            bigger_qty = cr.fetchone()[0]
            bigger_qty = int(bigger_qty)
            big_uom_qty = divmod(total_qty, bigger_qty)
            if  big_uom_qty:
                big_req_quantity = big_uom_qty[0]
                req_quantity = big_uom_qty[1]
                cr.execute("update stock_requisition_line set big_req_quantity=%s,req_quantity=%s where product_id=%s and line_id=%s", (big_req_quantity, req_quantity, product_id, ids[0],))
                                    
        return True    

            
class stock_requisition_line(osv.osv):  # #prod_pricelist_update_line
    _name = 'stock.requisition.line'
    _description = 'Request Line'
    
    def create(self, cr, uid, data, context=None):
        print 'data',data
        requisition_obj= self.pool.get('stock.requisition')
        line_id=data['line_id']
        line_ids = requisition_obj.search(cr, uid, [('id', '=', line_id)], context=context)
        requisition = requisition_obj.browse(cr,uid,line_ids,context)
        location_id=requisition.to_location_id.id
        product=data['product_id']
        product_data= self.pool.get('product.product').browse(cr, uid, product, context=context)
        cr.execute('select  SUM(COALESCE(qty,0)) qty from stock_quant where location_id=%s and product_id=%s and qty >0 group by product_id', (location_id, product,))
        qty_on_hand = cr.fetchone()
        if qty_on_hand:
            qty_on_hand = qty_on_hand[0]
        else:
            qty_on_hand = 0
        data['qty_on_hand']=qty_on_hand
        data['product_uom']= product_data.product_tmpl_id.uom_id.id
        data['big_uom_id']=product_data.product_tmpl_id.big_uom_id.id
        data['uom_ratio']=product_data.product_tmpl_id.uom_ratio
        return super(stock_requisition_line, self).create(cr, uid, data, context=context)
    
    def on_change_product_id(self,cr,uid,ids,product_id,to_location_id, context=None):
        values = {}
        qty_on_hand=0
        if to_location_id and product_id:
            cr.execute('select  SUM(COALESCE(qty,0)) qty from stock_quant where location_id=%s and product_id=%s and qty >0 group by product_id', (to_location_id, product_id,))
            qty_on_hand = cr.fetchone()
            if qty_on_hand:
                qty_on_hand = qty_on_hand[0]
            else:
                qty_on_hand = 0
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            values = {
                'product_uom': product.product_tmpl_id.uom_id and product.product_tmpl_id.uom_id.id or False,
                'uom_ratio': product.product_tmpl_id.uom_ratio,
                'big_uom_id': product.product_tmpl_id.big_uom_id and product.product_tmpl_id.big_uom_id.id or False,
                'qty_on_hand':qty_on_hand,
                'sequence':product.sequence,
            }
        return {'value': values}
        
    _columns = {                
        'line_id':fields.many2one('stock.requisition', 'Line', ondelete='cascade', select=True),
        'pre_order' :fields.related('line_id', 'pre_order', type='boolean', string='Pre Order'),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'req_quantity' : fields.float(string='Qty', digits=(16, 0)),
        'product_uom': fields.many2one('product.uom', 'Smaller UOM'),
        'product_uos': fields.many2one('product.uom', 'UOM'),#add for new uom
        #'product_uos_quantity' : fields.float(string='Qty', digits=(16, 0)),
        'product_quantity' : fields.float(string='Qty', digits=(16, 0)), #add for new uom qty
        'uom_ratio':fields.char('Packing Unit'),
         'remark':fields.char('Remark'),
        'big_uom_id': fields.many2one('product.uom', 'Bigger UOM',  help="Default Unit of Measure used for all stock operation."),
        'big_req_quantity' : fields.float(string='Qty', digits=(16, 0)),
        'sale_req_quantity' : fields.float(string='Small Req Qty', digits=(16, 0)),
        'addtional_req_quantity' : fields.float(string='Small Add Qty', digits=(16, 0)),
        'qty_on_hand':fields.float(string='Qty On Hand', digits=(16, 0)),
        'sequence':fields.integer('Sequence'),
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
