from datetime import datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp

class purchase_order(osv.osv):
    _inherit = "purchase.order"

    _columns = {
        'pr_ref' : fields.char('PR Ref'),        
        'eta' : fields.datetime('Expected Time Arrived'),
        'etd' : fields.datetime('Expected Time Departure'),
        'received_date': fields.datetime('Received Date'),
        'earning_date' : fields.datetime('Earning Date'),
        'lc_date': fields.date('L/C Date'),
        'permit_date': fields.date('Permit Date'),
        'remit_date': fields.date('Remit Balance Date'),
        'bl_date': fields.date('B/L Date'),
        'agent_date': fields.date('Agent Date'),
        'target_date': fields.date('Target Date'),
        'finished_date': fields.date('Finished Date'),
    }
    
purchase_order()


    
    
