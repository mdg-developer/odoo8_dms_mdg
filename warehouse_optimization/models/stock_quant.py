from openerp.osv import fields, osv
from openerp.tools.translate import _

class stock_quant(osv.osv):

    _inherit = "stock.quant"

    def update_stock_quant(self, cr, uid, context=None):
        cr.execute("select * from update_stock_quant()")