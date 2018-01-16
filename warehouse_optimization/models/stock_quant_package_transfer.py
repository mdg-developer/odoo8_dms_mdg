from openerp.osv import fields, osv
from openerp.tools.translate import _

class stock_quant_package_transfer(osv.osv):
    
    _name = "stock.quant.package.transfer"
    _inherit = "stock.quant.package"

stock_quant_package_transfer()