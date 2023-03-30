from openerp.osv import fields, osv

class product_supplier(osv.osv):
    _name = "product.supplier"
    _columns = {
        'name': fields.char('Name'),
    }

product_supplier()