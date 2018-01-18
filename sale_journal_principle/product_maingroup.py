from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class product_maingroup(osv.osv):
    _inherit = "product.maingroup"
    _columns = {
                'name': fields.char('Description'),
                #'property_account_payable': fields.many2one('account.account', 'Payable Control' , domain="[('type', '=', 'payable')]", help="This account will be used instead of the default one as the payable account for the current partner", required=True),
                'property_account_receivable': fields.many2one('account.account', 'Cash Sale Clearing' , domain="[('type', '=', 'receivable')]", help="This account will be used instead of the default one as the receivable account for the current partner", required=True),
                'property_account_receivable_control': fields.many2one('account.account', 'Receivable Control' , domain="[('type', '=', 'receivable')]", help="This account will be used instead of the default one as the receivable account for the current partner", required=True),
                'property_account_foc': fields.many2one('account.account', 'Foc Account' , domain="[('type', '=', 'other')]", help="This account will be used instead of the default one as the receivable account for the current partner", required=True),
                'property_account_discount': fields.many2one('account.account', 'Discount Account' , domain="[('type', '=', 'other')]", help="This account will be used instead of the default one as the receivable account for the current partner", required=True),
                #'property_account_payable_clearing': fields.many2one('account.account', 'Payable Clearing' , domain="[('type', '=', 'payable')]", help="This account will be used instead of the default one as the payable account for the current partner", required=True),
                'property_account_receivable_clearing': fields.many2one('account.account', 'Receivable Clearing' , domain="[('type', '=', 'receivable')]", help="This account will be used instead of the default one as the receivable account for the current partner", required=True),                
#                 'property_account_foc_cash': fields.many2one('account.account', 'Foc Cash Account' , domain="[('type', '=', 'other')]",  required=True),
#                 'property_account_foc_credit': fields.many2one('account.account', 'Foc Credit Account' , domain="[('type', '=', 'other')]",  required=True),
#                 'property_account_discount_cash': fields.many2one('account.account', 'Discount Cash Account' , domain="[('type', '=', 'other')]",  required=True),
#                 'property_account_discount_credit': fields.many2one('account.account', 'Discount Credit Account' , domain="[('type', '=', 'other')]",  required=True),
                }
product_maingroup()