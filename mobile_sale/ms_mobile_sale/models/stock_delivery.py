from openerp.osv import fields,osv

class stock_delivery(osv.osv):
    _name = "stock.delivery"
    
    _description = "Stock Delivery"
    _rec_name = 'so_ref_no'
    _columns = {
       'customer_id':fields.many2one('res.partner', 'Customer'),
        'date':fields.date('Date'),
        'status':fields.char('Status'),
        'delivery_line': fields.one2many('stock.delivery.line', 'stock_delivery_id', 'Delivery Order Lines'),
        'note':fields.text('Note'),
        'so_ref_no':fields.char('Sale Order No'),
        'm_status' : fields.char('Status'),
        'picking_ref_id':fields.many2one('stock.picking', 'Picking Ref'),
    
    }
    
    _defaults = {
                 'm_status' : 'draft'
    }  
    
    def action_convert_sd(self, cr, uid, ids, context=None):
        for stockdeli in self.browse(cr, uid, ids, context=context):            
            cr.execute('SELECT import_mobile_sd_to_server(%s,%s,%s)', (stockdeli['so_ref_no'], stockdeli.picking_ref_id.id, stockdeli['id']))
            cr.execute("update stock_delivery set m_status='done' where so_ref_no = %s and picking_ref_id = %s and id = %s", (stockdeli['so_ref_no'], stockdeli.picking_ref_id.id, stockdeli['id'],))
stock_delivery()


class stock_delivery_line(osv.osv):
    _name = "stock.delivery.line"
    _description = "Mobile Stock Delivery"

    _columns = {
       'product_id':fields.many2one('product.product', 'Product'),
        'product_uos_qty':fields.float('Quantity'),
         'product_delivered_qty':fields.float('Delivered Quantity'),
        'stock_delivery_id':fields.many2one('stock.delivery', 'Delivey Id'),
        'tablet_id':fields.many2one('tablets.information', 'Tablet Id'),
        
    }
    _defaults = {
                 'product_uos_qty':1.0,
                 'product_delivered_qty':1.0,
    }  
stock_delivery_line()