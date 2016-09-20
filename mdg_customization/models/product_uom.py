from openerp.osv import fields, osv

class product_uom(osv.osv):
    _inherit = 'product.uom'
    _columns = {
                'uom_ratio': fields.char('UoM Ratio'),
                }
product_uom()
