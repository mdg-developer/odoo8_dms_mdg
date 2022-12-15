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
        'short_name': fields.char('Product Short Name', size=33),
        'myanmar_name': fields.char('Product Myanmar Name', size=33),
        'city_lines':fields.many2many('res.city'),
#         'ecommerce_price': fields.float('Price'),
        'ecommerce_uom_id': fields.many2one('product.uom', 'UOM'),
        'delivery_id':fields.many2one('delivery.group', 'Delivery Group',required=False),
            }
       
class product_uom_price(osv.osv):
    _inherit = 'product.uom.price'
    
    _columns = {
        
        'for_ecommerce':fields.boolean('For E-Commerce' , default=True),

    }