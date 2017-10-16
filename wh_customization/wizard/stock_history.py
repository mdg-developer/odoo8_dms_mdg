from datetime import datetime
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _

class stock_history(osv.osv):
    _inherit = 'stock.history'