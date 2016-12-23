
from openerp.osv import osv, fields
from openerp.tools.translate import _

class foc_any_product(osv.osv):
    
    _name = 'foc.any.product'
    _description = "FOC Any Product" 

    def create_order_line(self, cr, uid, ids, context=None):
                
#         mod_obj = self.pool.get('ir.model.data')        
#         act_obj = self.pool.get('ir.actions.act_window')
        data = self.read(cr, uid, ids, context=context)[0]
        sale_order_obj = self.pool.get('sale.order')
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'sale.order',
             'form': data
            }
        order_id=datas['ids']
        one_product_id=data['one_product_id']
        two_product_id=data['two_product_id']        
        three_product_id=data['three_product_id']        
        one_product_qty=data['one_product_qty']        
        two_product_qty=data['two_product_qty']        
        three_product_qty=data['three_product_qty']     
        pro_qty=data['qty']     

        print 'order_Idddddddddddddddd',order_id

        
        if ids:
            order_line_obj = self.pool.get('sale.order.line')
            product_obj = self.pool.get('product.product')
            product_qty=one_product_qty+two_product_qty+three_product_qty
            if product_qty >pro_qty:
                    raise osv.except_osv(_('Warning'),
                                     _('Please Check Available Qty'))    
            else:               
                if one_product_id and one_product_qty >0:
                        print 'one_product_idone_product_id',one_product_id
                        product_x = self.pool.get('product.product').browse(cr, uid, one_product_id[0], context=context)
                        print 'product_xproduct_xproduct_x',product_x
                        order_line_obj.create(cr, uid, {
                                     'order_id':order_id[0],
                                     'product_id':product_x.id,
                                     'name':'[%s]%s' % (
                                                 product_x.default_code,
                                                 product_x.name,
                                                 ),
                                      'price_unit':0.00,
                                      'promotion_line':True,
                                      'sale_foc':True,  # sale_foc_discount
                                      'product_uom_qty':one_product_qty,
                                      'product_uom':product_x.uom_id.id
                                      }, context)                   
                        
                if two_product_id and two_product_qty >0:
                        print 'two_product_idone_product_id',two_product_id
                        product_x = product_obj.browse(cr, uid, two_product_id[0])
                        print 'product_xproduct_xproduct_xyyy',product_x
    
                        order_line_obj.create(cr, uid, {
                                     'order_id':order_id[0],
                                     'product_id':product_x.id,
                                     'name':'[%s]%s' % (
                                                 product_x.default_code,
                                                 product_x.name,
                                                 ),
                                      'price_unit':0.00,
                                      'promotion_line':True,
                                      'sale_foc':True,  # sale_foc_discount
                                      'product_uom_qty':two_product_qty,
                                      'product_uom':product_x.uom_id.id
                                      }, context)                
                        
                if three_product_id and three_product_qty >0:
                        product_x = product_obj.browse(cr, uid, three_product_id[0])
                        print 'product_xproduct_xproduct_x',product_x
                        order_line_obj.create(cr, uid, {
                                     'order_id':order_id[0],
                                     'product_id':product_x.id,
                                     'name':'[%s]%s' % (
                                                 product_x.default_code,
                                                 product_x.name,
                                                 ),
                                      'price_unit':0.00,
                                      'promotion_line':True,
                                      'sale_foc':True,  # sale_foc_discount
                                      'product_uom_qty':three_product_qty,
                                      'product_uom':product_x.uom_id.id
                                      }, context)
            return True                                    
                         
    
    def _get_one_product_id(self, cr, uid, context=None):
            cr.execute("select one_product_id from foc_any_product_temp")
            product_id = cr.fetchone()
            if product_id:
                product_id = product_id[0]
            else:
                product_id = False
            return product_id    
 
    def _get_two_product_id(self, cr, uid, context=None):
            cr.execute("select two_product_id from foc_any_product_temp")
            product_id = cr.fetchone()
            if product_id:
                product_id = product_id[0]
            else:
                product_id = False
            return product_id      
         
    def _get_three_product_id(self, cr, uid, context=None):
            cr.execute("select three_product_id from foc_any_product_temp")
            product_id = cr.fetchone()
            if product_id:
                product_id = product_id[0]
            else:
                product_id = False
            return product_id       
        
    def _get_qty(self, cr, uid, context=None):
            cr.execute("select qty from foc_any_product_temp")
            product_qty = cr.fetchone()
            if product_qty:
                product_qty = product_qty[0]
            else:
                product_qty = False
            return product_qty      
                     
    _columns = {
                'one_product_id': fields.many2one('product.product', 'Product',readonly=True),
                 'two_product_id': fields.many2one('product.product', 'Product',readonly=True),
                 'three_product_id': fields.many2one('product.product', 'Product',readonly=True),
                'one_product_qty': fields.integer('Qty'),
                'two_product_qty': fields.integer('Qty'),
                'three_product_qty': fields.integer('Qty'),
                'qty':fields.integer('Qty',readonly=True),
                }
    _defaults = {

            'one_product_id' : _get_one_product_id,
            'two_product_id' : _get_two_product_id,
            'three_product_id' : _get_three_product_id,
            'qty':_get_qty,
              }
foc_any_product()    

class foc_any_product_temp(osv.osv):
    _name = 'foc.any.product.temp'
    _description = "FOC Any Product Temp"     
    _columns = {
                 'one_product_id': fields.many2one('product.product', 'Product'),
                 'two_product_id': fields.many2one('product.product', 'Product'),
                 'three_product_id': fields.many2one('product.product', 'Product'),
                'order_id':fields.many2one('sale.order','Sale Order ID'),
                'qty':fields.integer('Qty',readonly=True)
                }
foc_any_product_temp()    
