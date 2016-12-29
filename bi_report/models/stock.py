from openerp import tools
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class stock_move(osv.osv):
    _inherit = "stock.move"
    
    def _quantity_weight(self, cr, uid, ids, name, arg, context=None):
        template_obj = self.pool.get('product.template')
        product_obj = self.pool.get('product.product')
        res = {}
        weight_viss = 0
        for m in self.browse(cr, uid, ids, context=context):
            for product in product_obj.browse(cr,uid,[m.product_id],context):
                template_id = product.product_tmpl_id
                for prod_temp in template_obj.browse(cr,uid,[template_id],context):
                    weight_viss = m.product_qty * prod_temp.weight_net
                    res[m.id] = weight_viss
        return res
    
    
    _columns = {
         'weight_viss': fields.function(_quantity_weight, type='float',string='weight_viss', digits_compute=dp.get_precision('weight')),
        },
