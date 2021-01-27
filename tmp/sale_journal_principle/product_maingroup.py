from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class product_maingroup(osv.osv):
    _inherit = "product.maingroup"
    _columns = {
                'name': fields.char('Description'),
                # 'property_account_payable': fields.many2one('account.account', 'Payable Control' , domain="[('type', '=', 'payable')]", help="This account will be used instead of the default one as the payable account for the current partner", required=True),
                'property_account_receivable': fields.many2one('account.account', 'Cash Sale Clearing' , domain="[('type', '=', 'receivable')]", help="This account will be used instead of the default one as the receivable account for the current partner", required=True),
                'property_account_receivable_control': fields.many2one('account.account', 'Receivable Control' , domain="[('type', '=', 'receivable')]", help="This account will be used instead of the default one as the receivable account for the current partner", required=True),
                'property_account_foc': fields.many2one('account.account', 'Foc Account' , domain="[('type', '=', 'other')]", help="This account will be used instead of the default one as the receivable account for the current partner", required=True),
                'property_account_discount': fields.many2one('account.account', 'Discount Account' , domain="[('type', '=', 'other')]", help="This account will be used instead of the default one as the receivable account for the current partner", required=True),
                # 'property_account_payable_clearing': fields.many2one('account.account', 'Payable Clearing' , domain="[('type', '=', 'payable')]", help="This account will be used instead of the default one as the payable account for the current partner", required=True),
                'property_account_receivable_clearing': fields.many2one('account.account', 'Receivable Clearing' , domain="[('type', '=', 'receivable')]", help="This account will be used instead of the default one as the receivable account for the current partner", required=True),
#                 'property_account_foc_cash': fields.many2one('account.account', 'Foc Cash Account' , domain="[('type', '=', 'other')]",  required=True),
#                 'property_account_foc_credit': fields.many2one('account.account', 'Foc Credit Account' , domain="[('type', '=', 'other')]",  required=True),
#                 'property_account_discount_cash': fields.many2one('account.account', 'Discount Cash Account' , domain="[('type', '=', 'other')]",  required=True),
#                 'property_account_discount_credit': fields.many2one('account.account', 'Discount Credit Account' , domain="[('type', '=', 'other')]",  required=True),
            'property_account_difference': fields.property(
                type='many2one',
                relation='account.account',
                string="Price Difference Account",
                help="This account will be used to value price difference between purchase price and cost price."),
            'property_donation_account': fields.property(
                type='many2one',
                relation='account.account',
                string="Donation Account",
                help="This account will be used to value price difference between purchase price and cost price."),
            'property_sampling_account': fields.property(
                type='many2one',
                relation='account.account',
                string="Sampling Account",
                help="This account will be used to value price difference between purchase price and cost price."),
            'property_uses_account': fields.property(
                type='many2one',
                relation='account.account',
                string="Uses Account",
                help="This account will be used to value price difference between purchase price and cost price."),
            'property_destruction_account': fields.property(
                type='many2one',
                relation='account.account',
                string="Destruction Account",
                help="This account will be used to value price difference between purchase price and cost price."),                
            'property_difference_receivable_account': fields.property(
                type='many2one',
                relation='account.account', domain="[('type', 'in', ('receivable','payable'))]",
                string="Difference Receivable Account",
                help="This account will be used to value price difference between purchase price and cost price."),
            'property_difference_payable_account': fields.property(
                type='many2one',
                relation='account.account', domain="[('type','in', ('receivable','payable'))]",
                string="Difference Payable Account",
                help="This account will be used to value price difference between purchase price and cost price."),
            'partner_id':fields.many2one('res.partner', 'Supplier', domain="[('supplier','=',True)]", required=True),
           'pricelist_id': fields.many2one('product.pricelist', 'FOC Price List', domain="[('type','=','sale')]" , required=True),
        'is_separate_transition':fields.boolean('Is Separate Transition',default=False),
                 
                    
                    }
product_maingroup()
