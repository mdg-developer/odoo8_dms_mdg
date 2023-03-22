from openerp.osv import fields, osv

class product_uom(osv.osv):
    _inherit = 'product.uom'
    _columns = {
        'weight_ratio': fields.integer('Weight Ratio')
    }
product_uom()
