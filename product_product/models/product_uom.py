from openerp.osv import fields, osv
class product_uom(osv.osv):
    _inherit = 'product.uom'
    _columns = {

                'product_template_ids': fields.many2one('product.template', 'Product Template'),


                }
product_uom()
