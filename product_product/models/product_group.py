from openerp.osv import fields, osv
    
class product_group(osv.osv):
    _name = "product.group"
    _columns = {
                'name': fields.char('Description'),
                }
product_group()