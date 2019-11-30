from openerp.osv import osv, fields
from openerp import netsvc
from openerp.tools.translate import _
from openerp import tools, api
import logging

from openerp.osv.expression import get_unaccent_wrapper
from openerp.tools.translate import _
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
            'sale_team':fields.many2one('crm.case.section', 'Sale Team'),
        }