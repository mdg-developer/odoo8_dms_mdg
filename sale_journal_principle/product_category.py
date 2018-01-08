from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class product_category(osv.osv):
    _inherit = "product.category"
    _columns = {
                'property_account_foc_cash': fields.many2one('account.account', 'FOC Cash Account' , required=True),
                'property_account_foc_credit': fields.many2one('account.account', 'FOC Credit Account' , required=True),
                'property_account_discount_credit': fields.many2one('account.account', 'Discount Credit Account' , required=True),
                'property_account_discount_cash': fields.many2one('account.account', 'Discount Cash Account' , required=True),
                'property_account_foc_principle_receivable': fields.many2one('account.account', 'FOC Principle Account Receivable' , domain="[('type', '=', 'receivable')]",  required=True),
                'property_account_discount_principle_receivable': fields.many2one('account.account', 'Discount Account Receivable' , domain="[('type', '=', 'receivable')]", required=True),
               }