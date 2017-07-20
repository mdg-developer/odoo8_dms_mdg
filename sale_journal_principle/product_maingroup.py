from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class product_maingroup(osv.osv):
    _inherit = "product.maingroup"
    _columns = {
                'name': fields.char('Description'),
                'property_account_payable': fields.many2one('account.account', 'Account Payable' , domain="[('type', '=', 'payable')]", help="This account will be used instead of the default one as the payable account for the current partner", required=True),
                'property_account_receivable': fields.many2one('account.account', 'Account Receivable' , domain="[('type', '=', 'receivable')]", help="This account will be used instead of the default one as the receivable account for the current partner", required=True),
                'property_account_foc': fields.many2one('account.account', 'Foc Account' , domain="[('type', '=', 'other')]", help="This account will be used instead of the default one as the receivable account for the current partner", required=True),
                'property_account_discount': fields.many2one('account.account', 'Discount Account' , domain="[('type', '=', 'other')]", help="This account will be used instead of the default one as the receivable account for the current partner", required=True),
                
                }
product_maingroup()