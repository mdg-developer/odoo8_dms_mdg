from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.osv.fields import _column
import xmlrpclib

class product_pricelist(osv.osv):
   
    _inherit = "product.pricelist"
    _columns = {
        'is_credit_claim_price':fields.boolean('Is Credit Note Claim Price',track_visibility='always'),        
             }

        