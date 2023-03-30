from openerp.osv import fields, osv

class product_brand(osv.osv):
    _name = "product.brand"
    _columns = {
        'name': fields.char('Name'),
    }

product_brand()