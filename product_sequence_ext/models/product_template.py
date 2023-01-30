from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class product_template(osv.osv):
    _inherit = 'product.template'

    _columns = {
        'sequence': fields.integer(string='Sequence', required=True),
    }