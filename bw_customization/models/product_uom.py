from openerp.osv import fields, osv

class product_uom(osv.osv):
    _inherit = 'product.uom'
    _columns = {
        'description': fields.char('Description') 
                }
product_uom()
