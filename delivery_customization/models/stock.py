from openerp.osv import fields,osv
from openerp.tools.translate import _

class stock_picking(osv.osv):
    _inherit = 'stock.picking'   

    _columns = {       
        'weight_uom_id': fields.many2one('product.uom', 'Unit of Measure', readonly="1",help="Unit of measurement for Weight",),
    }
    
class stock_move(osv.osv):
    _inherit = 'stock.move'    

    _columns = {        
        'weight_uom_id': fields.many2one('product.uom', 'Unit of Measure', readonly="1",help="Unit of Measure (Unit of Measure) is the unit of measurement for Weight",),
    }
    