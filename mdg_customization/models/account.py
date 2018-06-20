from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import except_orm, Warning, RedirectWarning
class account_bank_statement_line(osv.osv):
    _inherit = 'account.bank.statement.line'
    
    def get_currency_rate_line(self, cr, uid, st_line, currency_diff, move_id, context=None):
        if currency_diff < 0:
            account_id = st_line.partner_id.gain_account_id.id      
            # account_id = st_line.company_id.expense_currency_exchange_account_id.id
            if not account_id:
                raise osv.except_osv(_('Insufficient Configuration!'), _("You should configure the 'Loss Exchange Rate Account' in the accounting settings, to manage automatically the booking of accounting entries related to differences between exchange rates."))
        else:
            account_id = st_line.partner_id.loss_account_id.id      
            # account_id = st_line.company_id.income_currency_exchange_account_id.id
            if not account_id:
                raise osv.except_osv(_('Insufficient Configuration!'), _("You should configure the 'Gain Exchange Rate Account' in the accounting settings, to manage automatically the booking of accounting entries related to differences between exchange rates."))    
        return {
            'move_id': move_id,
            'name': _('change') + ': ' + (st_line.name or '/'),
            'period_id': st_line.statement_id.period_id.id,
            'journal_id': st_line.journal_id.id,
            'partner_id': st_line.partner_id.id,
            'company_id': st_line.company_id.id,
            'statement_id': st_line.statement_id.id,
            'debit': currency_diff < 0 and -currency_diff or 0,
            'credit': currency_diff > 0 and currency_diff or 0,
            'amount_currency': 0.0,
            'date': st_line.date,
            'account_id': account_id
            }

class account_voucher(osv.osv):
    _inherit = 'account.voucher'
    
    def _get_exchange_lines(self, cr, uid, line, move_id, amount_residual, company_currency, current_currency, context=None):
        '''
        Prepare the two lines in company currency due to currency rate difference.

        :param line: browse record of the voucher.line for which we want to create currency rate difference accounting
            entries
        :param move_id: Account move wher the move lines will be.
        :param amount_residual: Amount to be posted.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: the account move line and its counterpart to create, depicted as mapping between fieldname and value
        :rtype: tuple of dict
        '''
        if amount_residual > 0:
            account_id = line.voucher_id.partner_id.gain_account_id.id
           # account_id = line.voucher_id.company_id.expense_currency_exchange_account_id
            if not account_id:
                model, action_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 'account', 'action_account_form')
                msg = _("You should configure the 'Loss Exchange Rate Account' to manage automatically the booking of accounting entries related to differences between exchange rates.")
                raise openerp.exceptions.RedirectWarning(msg, action_id, _('Go to the configuration panel'))
        else:
            account_id = line.voucher_id.partner_id.loss_account_id.id
            # account_id = line.voucher_id.company_id.income_currency_exchange_account_id
            if not account_id:
                model, action_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 'account', 'action_account_form')
                msg = _("You should configure the 'Gain Exchange Rate Account' to manage automatically the booking of accounting entries related to differences between exchange rates.")
                raise openerp.exceptions.RedirectWarning(msg, action_id, _('Go to the configuration panel'))
        # Even if the amount_currency is never filled, we need to pass the foreign currency because otherwise
        # the receivable/payable account may have a secondary currency, which render this field mandatory
        if line.account_id.currency_id:
            account_currency_id = line.account_id.currency_id.id
        else:
            account_currency_id = company_currency <> current_currency and current_currency or False
        move_line = {
            'journal_id': line.voucher_id.journal_id.id,
            'period_id': line.voucher_id.period_id.id,
            'name': _('change') + ': ' + (line.name or '/'),
            'account_id': line.account_id.id,
            'move_id': move_id,
            'partner_id': line.voucher_id.partner_id.id,
            'currency_id': account_currency_id,
            'amount_currency': 0.0,
            'quantity': 1,
            'credit': amount_residual > 0 and amount_residual or 0.0,
            'debit': amount_residual < 0 and -amount_residual or 0.0,
            'date': line.voucher_id.date,
        }
        move_line_counterpart = {
            'journal_id': line.voucher_id.journal_id.id,
            'period_id': line.voucher_id.period_id.id,
            'name': _('change') + ': ' + (line.name or '/'),
            'account_id': account_id,
            'move_id': move_id,
            'amount_currency': 0.0,
            'partner_id': line.voucher_id.partner_id.id,
            'currency_id': account_currency_id,
            'quantity': 1,
            'debit': amount_residual > 0 and amount_residual or 0.0,
            'credit': amount_residual < 0 and -amount_residual or 0.0,
            'date': line.voucher_id.date,
        }
        return (move_line, move_line_counterpart)    
    
class account_invoice(osv.osv):
    _inherit = 'account.invoice'    
    
    def _get_paid_amount(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        paid_amount=0.0
        if context is None:
            context = {}       
                        
        for invoice in self.browse(cr, uid, ids, context=context):
            invoice_data=self.browse(cr, uid, invoice.id, context=context)
            if invoice_data.residual >0:
                paid_amount=invoice_data.amount_total - invoice_data.residual    
            res[invoice.id]= paid_amount            
        return res   
    
    _columns = {
                'pre_order': fields.boolean('Pre Order' , readonly=True),
               'branch_id':fields.many2one('res.branch', 'Branch'),
               'delivery_remark':fields.selection([
                    ('partial', 'Partial'),
                    ('delivered', 'Delivered'),
                    ('none', 'None')
               ], 'Deliver Remark', readonly=False, default='none'),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Pricelist for current sales invoice."),
         'code':fields.char('Customer ID', readonly=True),
        'street': fields.char('Street', readonly=True),
        'street2': fields.char('Street2', readonly=True),
        'city': fields.many2one('res.city', 'City', ondelete='restrict', readonly=True),
        'state_id': fields.many2one("res.country.state", 'State', ondelete='restrict', readonly=True),
        'country_id': fields.many2one('res.country', 'Country', ondelete='restrict', readonly=True),
        'township': fields.many2one('res.township', 'Township', ondelete='restrict', readonly=True),
        'payment_term' : fields.many2one('account.payment.term', string='Payment Terms',readonly=False,
        help="If you use payment terms, the due date will be computed automatically at the generation "
             "of accounting entries. If you keep the payment term and the due date empty, it means direct payment. "
             "The payment term may compute several due dates, for example 50% now, 50% in one month."),
        'paid_amount': fields.function(_get_paid_amount, type='char', string='Paid Amount',digits_compute= dp.get_precision('Product Price')),     
        'is_entry':fields.boolean('Is Entry'),
        'rebate_later': fields.boolean('Rebate Later', default=False, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
        'credit_allow':fields.boolean('Credit Allow',default=False),

}
        
    def on_change_payment_type(self, cr, uid, ids, partner_id, payment_type, context=None):
        values = {}
        print 'payment_type', payment_type
        if payment_type == 'cash':
            payment_term = 1
        elif payment_type == 'credit':
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
            payment_term = partner.property_payment_term and partner.property_payment_term.id or False
        else:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
            payment_term = partner.property_payment_term and partner.property_payment_term.id or False        
        values = {
             'payment_term':payment_term, }
        domain = {'payment_term': [('id', '=', payment_term)]}
        return {'value': values,'domain': domain}
    
    

account_invoice()   

