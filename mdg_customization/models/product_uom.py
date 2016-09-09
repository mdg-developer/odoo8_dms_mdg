from openerp.osv import fields, osv

class product_uom(osv.osv):
    _inherit = 'product.uom'
    _columns = {
                'uom_ratio': fields.char('UOM Ratio',required=True),
                }
product_uom()
