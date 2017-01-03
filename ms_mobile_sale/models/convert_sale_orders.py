from openerp.osv import fields, osv

class convert_sale_orders(osv.osv):
    _name = "mobile.sale.order"
    _description = "Mobile Sales Order"   
    _columns = {
        'name': fields.char('Order Reference', size=64),
        'partner_id':fields.many2one('res.partner', 'Customer'),
        'customer_code':fields.char('Customer Code'),
        'sale_plan_name':fields.char('Sale Plan Name'),
        'user_id':fields.many2one('res.users', 'Salesman Name'),
        'mso_latitude':fields.float('Geo Latitude'),
        'mso_longitude':fields.float('Geo Longitude'),
        'amount_total':fields.float('Total Amount'),
        'type':fields.selection([
                ('credit', 'Credit'),
                ('cash', 'Cash'),
                ('consignment', 'Consignment'),
                ('advanced', 'Advanced')
            ], 'Payment Type'),
        'delivery_remark':fields.selection([
                ('partial', 'Partial'),
                ('delivered', 'Delivered'),
                ('none', 'None')
            ], 'Deliver Remark'),
        'additional_discount':fields.float('Discount'),
        'deduction_amount':fields.float('Deduction Amount'),
        'paid_amount':fields.float('Paid Amount'),
        'paid':fields.boolean('Paid'),
          'void_flag':fields.selection([
                ('voided', 'Voided'),
                ('none', 'Unvoid')
            ], 'Void'),
        #'date':fields.date('Date'),
        #'date_order': fields.datetime('Date', required=True, readonly=True, select=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False),
        'date':fields.datetime('Date'),
        'note':fields.text('Note'),
        'order_line': fields.one2many('mobile.sale.order.line', 'order_id', 'Order Lines', copy=True),
        'delivery_order_line': fields.one2many('products.to.deliver', 'sale_order_id', 'Delivery Order Lines', copy=True),
        'tablet_id':fields.many2one('tablets.information', 'Tablet Id'),
        'sale_plan_day_id':fields.many2one('sale.plan.day', 'Sale Plan Day'),
        'sale_plan_trip_id':fields.many2one('sale.plan.trip', 'Sale Plan Trip'),
        'warehouse_id' : fields.many2one('stock.warehouse', 'Warehouse'),
        'sale_team':fields.many2one('crm.team', 'Sale Team'),
        'location_id'  : fields.many2one('stock.location', 'Location'),
        'm_status':fields.char('Status'),
        'due_date':fields.date('Due Date'),
        'payment_term': fields.many2one('account.payment.term', 'Payment Term'),
        #add promotion lines
       # 'promos_id':fields.one2many('promos.rules','mobile_sale_order_promo_rule_rel','sale_order_id','promo_id','Promotion'),
     'promos_line_ids':fields.one2many('mso.promotion.line','promo_line_id','Promotion Lines')                
    }
    _order = 'id desc'
    _defaults = {
        'date': fields.datetime.now,   
        'm_status' : 'draft',
       
    }

convert_sale_orders()

class mobile_sale_order_line(osv.osv):
    
    _name = "mobile.sale.order.line"
    _description = "Mobile Sales Order"

    _columns = {
        'product_id':fields.many2one('product.product', 'Products'),
        'product_uos_qty':fields.float('Quantity'),
        'price_unit':fields.float('Unit Price'),
        'discount':fields.float('Discount (%)'),
        'order_id': fields.many2one('mobile.sale.order', 'Sale Order'),
        'sub_total':fields.float('Sub Total'),
      
    }
    _defaults = {
       'product_uos_qty':1.0,
    }
mobile_sale_order_line()

class mobile_product_yet_to_deliver_line(osv.osv):
    
    _name = "products.to.deliver"
    _description = "Product Yet To Deliver"

    _columns = {
        'product_id':fields.many2one('product.product', 'Products'),
        'product_qty':fields.float('Quantity'),
        'product_qty_to_deliver':fields.float('Quantity To Deliver'),
        'sale_order_id': fields.many2one('mobile.sale.order', 'Sale Order'),
                }
mobile_product_yet_to_deliver_line()

class mso_promotion_line(osv.osv):
    _name='mso.promotion.line'
    _columns={
              'promo_line_id':fields.many2one('mobile.sale.order','Promotion line'),
              'pro_id': fields.many2one('promos.rules', 'Promotion Rule', change_default=True, readonly=False),
              'from_date':fields.datetime('From Date'),
              'to_date':fields.datetime('To Date')
              }
    def onchange_promo_id(self,cr,uid,ids,pro_id,context=None):
        result={}
        promo_pool=self.pool.get('promos.rules')
        datas= promo_pool.read(cr,uid,pro_id,['from_date','to_date'],context=context)

        if datas:
            result.update({'from_date':datas['from_date']})
            result.update({'to_date':datas['to_date']})
        return {'value':result}      
mso_promotion_line()