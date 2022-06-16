from openerp.osv import fields, osv

class product_uom(osv.osv):
    _inherit = 'product.uom'
    _columns = {
        'category_id': fields.many2one('product.uom.categ', 'UoM Category', required=True, ondelete='cascade',
            help="Conversion between Units of Measure can only occur if they belong to the same category. The conversion will be made based on the ratios."),                }
product_uom()
