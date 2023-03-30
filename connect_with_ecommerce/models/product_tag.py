from openerp.osv import fields, osv

class product_tag(osv.osv):
    _name = "product.tag"
    _columns = {
        'name': fields.char('Name'),
        'tag_id': fields.integer("Product Tag Id")
    }
# shl

product_tag()