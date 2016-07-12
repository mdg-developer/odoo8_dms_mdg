from openerp.osv import fields, osv
    
class product_principal(osv.osv):
    _name = "product.principal"
    _columns = {
                'name': fields.char('Description'),
                }
product_principal()