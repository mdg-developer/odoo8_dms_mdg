from openerp.osv import fields, osv
from openerp.tools.translate import _

class stock_location(osv.osv):

    _inherit = "stock.location"
    
    _columns = {
        'drop_point_location': fields.boolean('Drop Point Location'),
        'stickering_location': fields.boolean('Stickering Location'),
        'repacking_location': fields.boolean('Repacking Location'),
        'row': fields.char('Row'),
        'layer': fields.char('Layer'),
        'room': fields.char('Room'),
        'cell': fields.char('Cell'),
        'product_move_type_id': fields.many2one('product.move.type', 'Product Nature'),
        'maingroup_id': fields.many2one('product.maingroup', 'Principle'),
    }
