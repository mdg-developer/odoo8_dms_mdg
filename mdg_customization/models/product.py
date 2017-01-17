from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.osv.fields import _column

class product_product(osv.osv):
    _inherit = 'product.product'

class product_template(osv.osv):
    _inherit = 'product.template'
    _columns = {
        'is_foc':fields.boolean('FOC Item'),
                    }
        
