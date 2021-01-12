from openerp.osv import fields, osv
from datetime import datetime
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

class stock_location_group(osv.osv):
    _name = "stock.location.group"
    
    _columns = {
        'name': fields.char('Name'),
    }
    
stock_location_group()
