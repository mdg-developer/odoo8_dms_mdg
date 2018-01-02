from openerp.osv import fields, osv
import time
from openerp.tools.translate import _

class exchange_product(osv.osv):
    
    _name = "product.transactions"
    _description = "Exchange Product"
    _columns = {
                'transaction_id':fields.char('ID'),
                'customer_id':fields.many2one('res.partner', 'Customer Name'),
                'customer_code':fields.char('Customer Code',readonly=True),
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
#         product_line_obj = self.pool.get('product.transactions.line')
#         product_obj = self.pool.get('product.transactions')
#         picking_obj = self.pool.get('stock.picking')
#         move_obj = self.pool.get('stock.move')
#         if ids:
#             product_value = product_obj.browse(cr, uid, ids[0], context=context)
#             issue_date = product_value.date
#             location_id = product_value.customer_id.property_stock_customer.id
#             from_location_id = product_value.team_id.location_id.id
#             origin = product_value.transaction_id
#             cr.execute('select id from stock_picking_type where default_location_dest_id=%s and default_location_src_id = %s', (location_id, from_location_id,))
#             price_rec = cr.fetchone()
#             if price_rec: 
#                 picking_type_id = price_rec[0] 
#             else:
#                 raise osv.except_osv(_('Warning'),
#                                      _('Picking Type has not for this transition'))
#             picking_id = picking_obj.create(cr, uid, {
#                                           'date': issue_date,
#                                           'origin':origin,
#                                           'picking_type_id':picking_type_id}, context=context)
#             product_line_id = product_line_obj.search(cr, uid, [('transaction_id', '=', ids[0])], context=context)
#             if product_line_id and picking_id:
#                 for line_id in product_line_id:
#                     product_line_value = product_line_obj.browse(cr, uid, line_id, context=context)
#                     product_id = product_line_value.product_id.id
#                     name = product_line_value.product_id.name_template
#                     product_uom = product_line_value.uom_id.id
#                     origin = origin
#                     quantity = product_line_value.product_qty
#                     trans_type=product_line_value.trans_type
#                     if trans_type == 'In':
#                         move_id=move_obj.create(cr, uid, {'picking_id': picking_id,
#                                              'picking_type_id':picking_type_id,
#                                               'product_id': product_id,
#                                               'product_uom_qty': quantity,
#                                               'product_uos_qty': quantity,
#                                               'product_uom':product_uom,
#                                               'location_id':location_id,
#                                               'location_dest_id':from_location_id,
#                                               'name':name,
#                                                'origin':origin,
#                                               'state':'confirmed'}, context=context)     
#                     else:
#                         move_id=move_obj.create(cr, uid, {'picking_id': picking_id,
#                                              'picking_type_id':picking_type_id,
#                                               'product_id': product_id,
#                                               'product_uom_qty': quantity,
#                                               'product_uos_qty': quantity,
#                                               'product_uom':product_uom,
#                                               'location_id':from_location_id,
#                                               'location_dest_id':location_id,
#                                               'name':name,
#                                                'origin':origin,
#                                               'state':'confirmed'}, context=context)     
#                     move_obj.action_done(cr, uid, move_id, context=context)                            
#                 return self.write(cr, uid, ids, {'e_status':'done'}) 
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
