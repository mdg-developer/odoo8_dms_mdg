from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import timedelta,datetime
import calendar

class ProductReorder(osv.osv):
    _name = "product.reorder"
    
    _columns = {
               'partner_id': fields.many2one('res.partner', 'Customer'),  
               'product_id': fields.many2one('product.product', 'Product'), 
               'default_code':fields.char(string='Internal Reference'),  
               'quantity': fields.float('Quantity'),             
            }
