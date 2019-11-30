from openerp.osv import osv, fields
from openerp import netsvc
from openerp.tools.translate import _
from openerp import tools, api
import logging

from openerp.osv.expression import get_unaccent_wrapper
from openerp.tools.translate import _
# from pyfcm import FCMNotification

CONDITION = [    
    ('>=', _('greater than or equal to')),    
    ('<=', _('less than or equal to')),
]
 
class SaleOptionalPromotion(osv.Model):
    
    _name = "sale.optional.promotion"
    
    _columns = {             
            'product_id': fields.many2one('product.product', 'Product', required=True),
            'condition': fields.selection(CONDITION, 'Condition', required=True),
            'amount':fields.float('Amount', required=True),
            'quantity':fields.float('Quantity', required=True),
            'rule_id':fields.many2one('promos.rules', 'Rule'),            
        }