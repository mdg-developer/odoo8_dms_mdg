from openerp.osv import fields, osv
from openerp.tools.translate import _

class stock_picking(osv.osv):
    _inherit = "stock.picking"
    
    _columns = {
               'is_transfer_request':fields.boolean('Is Transfer Request'),
               }
    _defaults = {
        'is_transfer_request': False,
        }
