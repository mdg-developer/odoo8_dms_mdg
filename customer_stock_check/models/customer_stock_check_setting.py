from openerp.osv import fields , osv

class customer_stock_check(osv.osv):
    _name = "stock.check.setting"
    _description = "Customer Stock Check Setting"
    _rec_name = "outlet_type"
    _columns = {      
                'outlet_type': fields.many2one('outlettype.outlettype', 'Outlet Type'), 
                'date': fields.date('Checked Date'),   
                'stock_setting_line':fields.one2many('stock.check.setting.line', 'stock_setting_ids', string='Product',copy=True),
    }    
    
    def retrieve_stock(self, cr, uid, ids, context=None):  
        stock_line_obj = self.pool.get('stock.check.setting.line')
        if ids:
            cr.execute("""select pp.id,pp.sequence from product_product pp,product_template pt
                where pp.product_tmpl_id = pt.id and pt.type!='service' and pt.is_foc !=True and pt.active='True'
                and pp.active='True' and pp.id not in (select product_id from stock_check_setting_line where stock_setting_ids =%s) order by pp.sequence asc""",(ids[0],))
            product_data = cr.fetchall()
            for p_line in product_data:
                if p_line:
                    product_id = p_line[0]
                    sequence = p_line[1]
                    stock_line_obj.create(cr, uid, {'stock_setting_ids': ids[0],
                                'sequence':sequence,
                                'product_id': product_id, 
                                }, context=context)
        return True 
customer_stock_check()

class customer_stock_check_line(osv.osv):    
    _name = 'stock.check.setting.line'      
    
    _columns = {
                'stock_setting_ids': fields.many2one('stock.check.setting', 'Partner Stock Check Setting'),
                'sequence':fields.integer('Sequence'),                 
                'product_id':fields.many2one('product.product', 'Product'),
                'available': fields.boolean('Available',default=False),
                'product_uom_qty':fields.boolean('QTY',default=False),
                'facing':fields.boolean('Facing',default=False),    
                'chiller':fields.boolean('Chiller',default=False),          
      
                }
customer_stock_check_line()    