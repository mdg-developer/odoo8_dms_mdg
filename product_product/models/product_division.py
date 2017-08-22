from openerp.osv import fields, osv
class product_division(osv.osv):
    _name = "product.division"
    _columns = {
                'name': fields.char('Description'),
                }
product_division()