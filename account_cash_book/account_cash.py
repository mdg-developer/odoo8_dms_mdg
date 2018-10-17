import time
from openerp.osv import fields, osv
from openerp.tools import float_compare
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class account_bank_statement_line(osv.osv):

    _inherit = 'account.bank.statement.line'
    _order = 'sequence'
    _columns = {
            'name': fields.text('Communication', required=True),
         #   'department_id':fields.many2one('account.department', 'Department'),
            'sequence': fields.integer('No.' , readonly=True),
            'date': fields.date('Date'),
            'account_id': fields.many2one('account.account', 'Account' , required=True),
            'income_amt': fields.float('Income', digits_compute=dp.get_precision('Account')),
            'expense_amt': fields.float('Expenses', digits_compute=dp.get_precision('Account')),
        }

    def create(self, cursor, user, vals, context=None):
        sequence = self.pool.get('ir.sequence').get(cursor, user,
            'cash.code') or '/'
        vals['sequence'] = sequence
        if vals.get('amount_currency', 0) and not vals.get('amount', 0):
            raise osv.except_osv(_('Error!'), _('If "Amount Currency" is specified, then "Amount" must be as well.'))
        return super(account_bank_statement_line, self).create(cursor, user, vals, context=context)
    
    def onchange_income_amt(self, cr, uid, ids, income_amt, context=None):
        val = {'amount': 0.0}
        if income_amt:
            amount = income_amt
            val['amount'] = amount
        return {'value': val}        
    
    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        partner_obj=self.pool.get('res.partner')
        val = {'account_id': False}
        if partner_id:
            partner_Data=partner_obj.browse(cr, uid, partner_id, context=context)
            customer=partner_Data.customer
            supplier=partner_Data.supplier
            cr.execute('select property_account_receivable from product_maingroup')
            if supplier ==True:
                cr.execute('select property_account_payable from product_maingroup')
                account_id=cr.fetchone()[0]
            if customer==True:
                cr.execute('select property_account_receivable from product_maingroup')
                account_id=cr.fetchone()[0]

            val['account_id'] = account_id
        return {'value': val}            
    
    def onchange_expense_amt(self, cr, uid, ids, expense_amt, context=None):
        val = {'amount': 0.0}
        if expense_amt:
            amount = expense_amt
            val['amount'] = -amount
        return {'value': val}   
 
 
class account_bank_statement(osv.osv):

    _inherit = 'account.bank.statement'
    _columns = {
                            'brand_id' :fields.many2one('res.branch', 'Branch'),
                            }
