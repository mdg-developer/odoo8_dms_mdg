from openerp.osv import fields, osv
import time

class exchange_product(osv.osv):
    
    _name = "product.transactions"
    _description = "Exchange Product"

    _columns = {
                'transaction_id':fields.char('ID'),
                'customer_id':fields.many2one('res.partner', 'Customer Name'),
                'customer_code':fields.char('Customer Code'),
                'team_id'  : fields.many2one('crm.case.section', 'Sale Team'),
                'date':fields.date('Date'),
              'exchange_type':fields.selection([('Exchange', 'Exchange'), ('Color Change', 'Color Change'), ('Sale Return', 'Sale Return'), ], 'Type'),
                'item_line': fields.one2many('product.transactions.line', 'transaction_id', 'Items Lines', copy=True),
                'void_flag':fields.selection([('none', 'Unvoid'), ('voided', 'Voided')], 'Void Status'),
                'location_id'  : fields.many2one('stock.location', 'Location', required=True),
                'e_status':fields.char('Status'),
                                'note':fields.text('Note'),

    }
    
    _defaults = {        
                 'e_status' : 'draft',
                 }
    
    def onchange_customer_id(self, cr, uid, ids, customer_id, context=None):
        
        result = {}
        res_partner = self.pool.get('res.partner')
        datas = res_partner.read(cr, uid, customer_id, ['customer_code'], context=context)
        print 'datas', datas
        if datas:
            result.update({'customer_code':datas['customer_code']})            
        return {'value':result} 
         
#     def action_convert_ep(self, cr, uid, ids, context=None):
#         
#         self.write(cr, uid, [ids[0]], {'state': 'wh_approve','date':time.strftime('%Y/%m/%d')})
#         print 'ids',ids
#         product_line_obj = self.pool.get('product.transactions.line')
#         requisition_obj = self.pool.get('product.transactions')
#         picking_obj = self.pool.get('stock.picking')
#         move_obj = self.pool.get('stock.move')
#         
#         req_value= req_lines ={}
#         if ids:
#             cr.execute("update product_transactions set e_status='done' where id = %s ", (ids[0],))
#             print 'done'
#             req_value = requisition_obj.browse(cr,uid,ids[0],context=context)
#             transfer_date = req_value.date
#             location_id = 9
#             form_location_id = req_value.location_id.id
#             origin = ''
#             partner_id = req_value.customer_id
#             origin=req_value.exchange_type
#           #  print 'customer_id', partner_id
#             cr.execute('select id from stock_picking_type where default_location_dest_id=%s and name like %s',(location_id,'%Internal Transfer%',))
#             price_rec = cr.fetchone()
#             
#             if price_rec: 
#                 picking_type_id = price_rec[0] 
#             else :
#                 picking_type_id = 33
#            # print 'customer_id1111', picking_type_id
#                 
#             req_id1 = picking_obj.create(cr, uid, {'partner_id': partner_id.id,
#                                           'date': transfer_date,
#                                           'origin':origin,
#                                           'picking_type_id':picking_type_id}, context=context)
#            # print 'customer_id1234', req_id1
#             
#             req_id = product_line_obj.search(cr,uid,[('transaction_id','=',ids[0])],context=context)
#             
#             if req_id and req_id1:
#                 print 'req_id',req_id
#                 for id in req_id:
#                     req_value = product_line_obj.browse(cr,uid,id,context=context)
#                     product_id = req_value.product_id.id
#                     quantity = req_value.product_qty
#                     #print 'quantity',quantity
#                     name = req_value.product_id.name_template
#                     type=req_value.trans_type
#                    # print 'type',type
#                     if (type=='In'):
#                         print  'IN',type
#                     else:
#                         if (quantity >0):
#                             quantity=quantity* (-1)
#                     cr.execute('select uom_id  from product_template t join product_product p on p.product_tmpl_id=t.id where p.id=%s group by uom_id',(product_id,))        
#                     ids = cr.fetchall()
#                     #print 'tzt', ids
#                     if quantity>0:
#                         print 'product_id',product_id 
#                         move_obj.create(cr, uid, {'picking_id': req_id1,
#                                                   'product_id': product_id,
#                                                   'product_uom_qty': quantity,
#                                                   'product_uom':ids[0],
#                                                   'location_id':location_id,
#                                                   'location_dest_id':form_location_id,
#                                                   'name':name,
#                                                    'origin':origin,
#                                                   'state':'confirmed',
#                                                   'company_id':1}, context=context)
#                     elif quantity<0:
#                         print 'less than'
#                         move_obj.create(cr, uid, {'picking_id': req_id1,
#                                                   'product_id': product_id,
#                                                   'product_uom_qty':req_value.product_qty,
#                                                   'product_uom':ids[0],
#                                                   'location_id':form_location_id,
#                                                   'location_dest_id':location_id,
#                                                   'name':name,
#                                                    'origin':origin,
#                                                   'state':'confirmed',
#                                                   'company_id':1}, context=context)
#                 print 'move_objmove_objmove_obj',move_obj
#                 print 'req_id1',req_id1       
#                 cr.execute("update stock_picking set state='done' where id=%s",(req_id1,))
#                 cr.execute("select id from stock_move where picking_id=%s",(req_id1,))
#                 id=cr.fetchall()
#                 print id
#                 for move_id in id:
#                     print 'idddddddddd',move_id
#                     if move_id:
#                         move_obj.action_done(cr, uid, move_id[0], context=context) 

exchange_product()

class exchange_product_line_item(osv.osv):
    
    _name = "product.transactions.line"
    _description = "Exchange Product"

    _columns = {
                'transaction_id': fields.many2one('product.transactions', 'Form,'),
                'product_id':fields.many2one('product.product', 'Product'),
                'uom_id': fields.many2one('product.uom', 'UOM', required=True, help="Default Unit of Measure used for all stock operation."),
                'product_qty':fields.integer('Qty'),
                'so_No':fields.char('SO Reference'),
                'trans_type':fields.selection([('In', 'In'), ('Out', 'Out')], 'Type', required=True),
                'transaction_name':fields.char('Transaction Name'),
                'note':fields.char('Note'),
                'exp_date':fields.date('Expired Date'),
                'batchno':fields.char('Batch No'),
                }
    
exchange_product_line_item()
