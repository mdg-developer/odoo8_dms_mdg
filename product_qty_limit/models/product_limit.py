from openerp.osv import fields, osv


class product_limit(osv.osv):
    _name = "product.limit"
    _columns = {
        'product_id': fields.many2one('product.template', 'Product'),
        'max_qty':fields.integer('Max Qty'),
    }


product_limit()