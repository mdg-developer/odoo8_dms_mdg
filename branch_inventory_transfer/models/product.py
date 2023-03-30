from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.osv.fields import _column


class product_template(osv.osv):
    _inherit = 'product.template'
    _columns = {
         'viss_value': fields.float('Viss', digits_compute=dp.get_precision('Cost Price')),
         'cbm_value': fields.float('CBM', digits_compute=dp.get_precision('Cost Price')),
         'ctn_pallet': fields.float('Ctn/Pallet'),
         'ti': fields.float('TI'),
         'hi': fields.float('HI'),
         'ctn_weight': fields.float('Carton Weight'),
         'ctn_height': fields.float('Carton Height'),
         'inbound_shelf_life': fields.float('Inbound Shelf Life'),
         'inbound_shelf_life_min': fields.float('Inbound Shelf Life (Min Days)'),
         'kg_value': fields.float('Kg')
        }
    def on_change_kg_value(self, cr, uid, ids, kg_value, context=None):
        viss_value = kg_value / 1.63
        return {'value':{'viss_value':viss_value}}
    