from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class product_template(osv.osv):
    _inherit = 'product.template'

    _columns = {
        'sequence': fields.integer(string='Sequence', required=True),
    }

class product_product(osv.osv):
    _inherit = "product.product"

    _columns = {
        'sequence': fields.related('product_tmpl_id', 'sequence', type='integer', string='Sequence', store=True),
    }