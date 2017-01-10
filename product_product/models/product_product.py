from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp import SUPERUSER_ID

class product_product(osv.osv):
    _inherit = "product.product"
    _columns = {
        'sequence': fields.integer('Sequence', size=3, default=0),
        }    
    _sql_constraints = [('default_code_uniq', 'unique(default_code)',
                                  'Product Code should not be same to others!')
                    ]    
