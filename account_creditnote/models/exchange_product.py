from openerp.osv import fields, osv
import time
from openerp.tools.translate import _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class exchange_product(osv.osv):
    
    _inherit = "product.transactions"
    
    _columns = {

              'exchange_type':fields.selection([('Exchange', 'Exchange'), ('Sale Return', 'Sale Return'),('Sale Return with Credit Note', 'Sale Return with Credit Note') ], 'Type',required=True),
              }