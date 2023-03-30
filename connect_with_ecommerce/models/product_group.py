from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.osv.fields import _column
import xmlrpclib
# shl
class product_group(osv.osv):
    _inherit = 'product.group'

    _columns={
        'category_id':fields.many2one('product.category','Product Category')
    }