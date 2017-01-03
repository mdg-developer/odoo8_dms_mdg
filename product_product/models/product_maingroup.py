from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class product_maingroup(osv.osv):
    _name = "product.maingroup"
    _columns = {
                'name': fields.char('Description'),
                }
product_maingroup()