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
        'list_price': fields.float('Sale Price',digits_compute=dp.get_precision('Product Price')),
                }