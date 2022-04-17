from openerp.osv import fields, osv
from openerp.tools.translate import _

class stock_warehouse(osv.osv):
    _inherit = "stock.warehouse"

        
    _columns = {
                'code': fields.char('Short Name', size=10, required=True, help="Short name used to identify your warehouse"),
               }