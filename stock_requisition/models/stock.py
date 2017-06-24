from openerp.osv import fields, osv
from datetime import datetime
from openerp.tools.translate import _
from openerp.fields import Many2one
from openerp import tools

class stock_move(osv.osv):
    
    _inherit = 'stock.move'
    _columns = {
                'manual': fields.boolean('Manual'),        
               }
