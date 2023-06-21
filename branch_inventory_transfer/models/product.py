from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.osv.fields import _column


class product_template(osv.osv):
    _inherit = 'product.template'
    _columns = {
         'viss_value': fields.float('Big UOM Weight (Viss)', digits_compute=dp.get_precision('Cost Price')),
         'cbm_value': fields.float('Big UOM (cm3)', digits_compute=dp.get_precision('Cost Price')),
         'ctn_pallet': fields.float('Ctn/Pallet(Racking)'),
         'ti': fields.float('TI'),
         'hi': fields.float('HI'),
         'ctn_weight': fields.float('Big UOM Weight (Kg)'),
         'ctn_height': fields.float('Big UOM (H) cm'),
         'inbound_shelf_life': fields.float('Inbound Shelf Life'),
         'inbound_shelf_life_min': fields.float('Inbound Shelf Life (Min Days)'),
         'small_uom_weight': fields.float('Small UOM Weight(Kg)'),
         'big_uom_length': fields.float('Big UOM (L) cm'),
         'big_uom_breadth': fields.float('Big UOM (B) cm'),
         'ctn_pallet_pickface': fields.float('Ctn/Pallet (Pickface)'),
        }

    def on_change_ti_hi(self, cr, uid, ids, ti, hi, context=None):
        pallet_value = ti * hi
        return {'value':{'ctn_pallet':pallet_value}}

    def on_change_lenght_breadth_height(self, cr, uid, ids, big_uom_length, big_uom_breadth, ctn_height, context=None):
        cbm_value = big_uom_length * big_uom_breadth * ctn_height
        return {'value':{'cbm_value': cbm_value}}
    
    def on_change_ctn_value(self, cr, uid, ids, ctn_value, context=None):
        viss_value = ctn_value / 1.63
        return {'value':{'viss_value':viss_value}}
    