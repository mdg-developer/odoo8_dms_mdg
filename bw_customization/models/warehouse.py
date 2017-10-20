from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.osv.fields import _column

class product_product(osv.osv):
    _inherit = 'stock.warehouse'
    
    _columns = {'issued_location': fields.many2one('stock.location', 'Issued Location',required=True),
            }