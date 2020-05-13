from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.osv.fields import _column
import xmlrpclib

class product_product(osv.osv):
    _inherit = "product.product"
    _columns = {
         'is_sync_ecommerce':fields.boolean('Is Sync Ecommerce',default=False),

        }    
class product_template(osv.osv):
    _inherit = 'product.template' 
    _columns = {
        'is_sync_ecommerce': fields.related('product_variant_ids', 'is_sync_ecommerce', type='boolean', string='Is Sync Ecommerce', required=False),

             }
       