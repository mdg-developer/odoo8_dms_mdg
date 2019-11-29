from openerp.osv import osv, fields
from openerp import netsvc
from openerp.tools.translate import _
from openerp import tools
import logging
# from pyfcm import FCMNotification
 
class SaleOptionalPromotion(osv.Model):
    "Sale Optional Promotion "
    _name = "sale.optional.promotion"
    
    _columns = {               
        
            'product_id': fields.many2one('product.product', 'Product'),
            'condition': fields.selection([('greater_than', '>'), ('less_than', '<'), ('between', 'Between')], "Condition"),
            'amount':fields.float('Amount'),
            'quantity':fields.float('Quantity'),
            'rule_id':fields.many2one('promos.rules', 'Rule'),
        }