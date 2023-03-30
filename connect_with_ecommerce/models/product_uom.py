from openerp.osv import fields, osv

class product_uom(osv.osv):
    _inherit = 'product.uom'
    _columns = {
        'uom_myanmar':fields.char('Unit of Measure (Myanmar)'),
        'uom_description': fields.char('Unit of Measure Description')
        }
product_uom()
