from openerp.osv import fields, osv
from datetime import datetime
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

class stock_location(osv.osv):
    _inherit = "stock.location"
    
    _columns = {
                'stock_location_group_id': fields.many2one('stock.location.group', 'Location Group'),
    }