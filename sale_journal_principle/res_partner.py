from openerp.osv import fields, osv
from openerp import tools
from openerp.tools.translate import _

class res_partner(osv.osv):
    _inherit = 'res.partner'
    
    _columns = {
                'property_account_payable': fields.many2one('account.account', 'Payable Control' , domain="[('type', '=', 'payable')]", help="This account will be used instead of the default one as the payable account for the current partner", required=True),                
                'property_account_payable_clearing': fields.many2one('account.account', 'Payable Clearing' , domain="[('type', '=', 'payable')]", help="This account will be used instead of the default one as the payable account for the current partner", required=True),  
               }