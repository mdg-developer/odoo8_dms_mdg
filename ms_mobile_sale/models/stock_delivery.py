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
    
    def product_qty_in_stock(self, cr, uid, warehouse_id , context=None, **kwargs):
        cr.execute("""
                    select product.id as product_id,sum(qty) as qty_on_hand  
from 
stock_quant quant, product_product product,
product_template product_temp
where quant.location_id = %s
and quant.product_id = product.id
and product.product_tmpl_id = product_temp.id
and product.active = true
 group by quant.product_id, main_group,name_template,product.id  order by name_template
            """, (warehouse_id,))
        datas = cr.fetchall()
        return datas
    
    def stock_delivery_line(self, cr, uid, pick_id , context=None, **kwargs):
        cr.execute(""" select sm.product_id,sum(sm.product_uos_qty) as product_uos_qty  
                        from stock_move sm , stock_picking sp
                        where sm.picking_id = sp.id
                        and sm.state ='assigned'
                        and sp.id = %s
                        group by sp.name ,sm.partner_id ,sm.date::date ,sm.product_id
                    """, (pick_id,))
                                
        datas = cr.fetchall()
        return datas
    
    def stock_delivery(self, cr, uid, user_id, context=None, **kwargs):
        cr.execute("""select sm.origin as so_name, sm.partner_id ,sm.date::date,
                        sm.tb_ref_no,sp.id as pick_id ,
                        sp.name as pick_name,sp.tranc_type
                        from stock_move sm , stock_picking sp
                        where sm.picking_id = sp.id
                        and sm.state ='assigned'
                        and sp.create_uid = %s
                        group by sp.id,sm.origin ,sm.partner_id ,sm.date::date,
                        sm.tb_ref_no ,sp.tranc_type ,sp.name
                        """, (user_id,))
                                
        datas = cr.fetchall()
        return datas

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