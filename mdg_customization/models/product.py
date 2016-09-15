from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class product_template(osv.osv):
    _inherit = 'product.template'
    _columns = {
        'big_uom_id': fields.many2one('product.uom', 'Bigger UOM', required=True, help="Default Unit of Measure used for all stock operation."),
        'is_foc':fields.boolean('Is FOC'),
        'big_list_price': fields.float('Bigger Price', digits_compute=dp.get_precision('Product Price'), help="Base price to compute the customer price. Sometimes called the catalog price."),
        'list_price': fields.float('Smaller Price', digits_compute=dp.get_precision('Product Price'), help="Base price to compute the customer price. Sometimes called the catalog price."),
                    }
    
    def _get_uom_id(self, cr, uid, *args):
        return self.pool["product.uom"].search(cr, uid, [], limit=1, order='id')[0]
    
    _defaults = {
        'big_uom_id': _get_uom_id,
       
    }
    
class product_pricelist_item(osv.osv):
    _inherit = "product.pricelist.item"
    _description = "Pricelist Item"        
    _columns = {
        'list_price': fields.float('Basic Price',digits_compute=dp.get_precision('Product Price')),
        'new_price': fields.float('New Price',
            digits_compute= dp.get_precision('New Price')),
                }

    def product_id_change(self, cr, uid, ids, product_id, context=None):
        if not product_id:
            return {}
        prod = self.pool.get('product.product').read(cr, uid, [product_id], ['code','name','product_tmpl_id'])
        product_tmpl_id = prod[0]['product_tmpl_id'][0]
        temp = self.pool.get('product.template').read(cr,uid,[product_tmpl_id],['list_price'])
        product_price = temp[0]['list_price']
      
        if prod[0]['code']:
            return {'value': {'name': prod[0]['code'],'new_price': product_price,'list_price':product_price}
                 
                    }
        return {}
    def price_dis_change(self, cr, uid, ids,product_id,price_discount,new_price,price_surcharge, context=None):
        
        if not product_id:
            return {}
        prod = self.pool.get('product.product').read(cr, uid, [product_id], ['code','name','product_tmpl_id'])
        product_tmpl_id = prod[0]['product_tmpl_id'][0]
        temp = self.pool.get('product.template').read(cr,uid,[product_tmpl_id],['list_price'])
        product_price = temp[0]['list_price']
        
        if price_discount:
            new_price = (product_price * (1+price_discount))+price_surcharge
            return {'value':{'new_price':new_price}}
        return {}
    def price_subcharge_change(self, cr, uid, ids,product_id, price_discount,new_price,price_surcharge, context=None):
        if not product_id:
            return {}
        prod = self.pool.get('product.product').read(cr, uid, [product_id], ['code','name','product_tmpl_id'])
        product_tmpl_id = prod[0]['product_tmpl_id'][0]
        temp = self.pool.get('product.template').read(cr,uid,[product_tmpl_id],['list_price'])
        product_price = temp[0]['list_price']
        if price_surcharge:
            new_price = (product_price * (1+price_discount))+price_surcharge
            return {'value':{'new_price':new_price}}
        return {}