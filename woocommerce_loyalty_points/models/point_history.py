from openerp.osv import fields, osv

class point_history(osv.osv):
    
    _name = "point.history"
    
    _columns = {
            'partner_id':fields.many2one('res.partner', 'Customer'),            
            'date':fields.date('Date'),
            'redeem_point':fields.integer('Redeem Point'),
            'balance_point':fields.integer('Balance Point'),
            'getting_point':fields.integer('Getting Point per Order'),
            'membership_id':fields.many2one('membership.config', 'Membership Level'),      
            'order_id':fields.many2one('sale.order', 'Sale Order'),     
    }


    def create_from_woo(self, cr, uid, ids, vals, context=None):
        partner_obj = self.pool.get('res.partner')             
        sale_order_obj = self.pool.get('sale.order')
        
        #Customer
        if vals.get('partner_id'):
            customer_value = partner_obj.search(cr, uid, [('customer_code','=',vals['partner_id'])], context=context)
            if customer_value:
                customer = partner_obj.browse(cr, uid, customer_value, context=context)
                vals['partner_id'] = customer.id

        #Order
        if vals.get('order_id'):
            so_value = sale_order_obj.search(cr, uid, [('woo_order_id','=',vals['order_id'])], context=context)
            if so_value:
                sale_order = partner_obj.browse(cr, uid, so_value, context=context)
                vals['order_id'] = sale_order.id                
        
        result = self.create(cr, uid, vals, context=context)
        return result
           
