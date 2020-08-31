from openerp.osv import fields, osv
from openerp.tools.translate import _

class res_city(osv.osv):
    _inherit = "res.city"
    
    _columns = {
               'delivery_team_id':fields.many2one('crm.case.section', 'Delivery Team',required=False),
               }
    
    def get_stock_status_label(self, cr, uid, ids, city_name=None, township_name=None, product_code=None, context=None):

        city_obj = self.pool.get('res.city')        
        product_obj = self.pool.get('product.product')
        if city_name and product_code:
            city_data = city_obj.search(cr, uid, [('name', '=', city_name)], context=context)            
            if city_data:
                city = city_obj.browse(cr, uid, city_data, context=context)
                if city.delivery_team_id:
                    issue_location = city.delivery_team_id.issue_location_id.id                    
                    product_data = product_obj.search(cr, uid, [('default_code', '=', product_code)], context=context)
                    if product_data:
                        product = product_obj.browse(cr, uid, product_data, context=context)    
                        cr.execute('''select COALESCE(sum(qty),0)
                                    from stock_quant
                                    where product_id=%s
                                    and location_id=%s''',(product.id,issue_location,))
                        quantity = cr.fetchall()                         
                        if quantity:
                            if quantity[0][0] > 0:
                                return 'in stock'
                            else:
                                return 'out of stock'
                    else:
                        return 'Product is not available'
                    
                                    