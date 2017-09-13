
import time
from datetime import datetime

from openerp import workflow
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import tools
from openerp.report import report_sxw
import openerp

class account_move_line(osv.osv):
    _inherit = "account.move.line"
     
#     def _get_paid_amount(self, cr, uid, ids,  context=None):
#         account_move_line = self.browse(cr, uid, ids, context=context)
#         account_invoce =  self.pool.get('account.invoice').browse(cr, uid,account_move_line.move_id, context=context)
#        
#         res = {}
#         paid_amount=0.0
#         if context is None:
#             context = {}       
#                          
#         for invoice in account_invoce:
#             invoice_data=self.browse(cr, uid, invoice.id, context=context)
#             if invoice_data.residual >0:
#                 paid_amount=invoice_data.amount_total - invoice_data.residual    
#             self.paid_amount = paid_amount            
#         #return res   
#      
# #     @api.one
# #     @api.depends('invoice_line.price_subtotal', 'tax_line.amount')
#     def _compute_total_amount(self, cr, uid, ids,  context=None):
#         account_move_line = self.browse(cr, uid, ids, context=context)
#         account_invoce =  self.pool.get('account.invoice').browse(cr, uid,account_move_line.move_id, context=context)
#        
#         for line in account_invoce.invoice_line:
#             line.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line)
#             line.amount_tax = sum(line.amount for line in self.tax_line)
#             self.amount_total = self.amount_untaxed + self.amount_tax
#         print 'self.amount_total>>',self.amount_total
#     
#     def _compute_residual(self, cr, uid, ids,  context=None):
#         self.residual = 0.0
#         # Each partial reconciliation is considered only once for each invoice it appears into,
#         # and its residual amount is divided by this number of invoices
#         
#         account_move_line = self.browse(cr, uid, ids, context=context)
#         account_invoce =  self.pool.get('account.invoice').browse(cr, uid,account_move_line.move_id, context=context)
#         
#         partial_reconciliations_done = []
#         for line in account_invoce.sudo().move_id.line_id:
#             if line.account_id.type not in ('receivable', 'payable'):
#                 continue
#             if line.reconcile_partial_id and line.reconcile_partial_id.id in partial_reconciliations_done:
#                 continue
#             # Get the correct line residual amount
#             if line.currency_id == self.currency_id:
#                 line_amount = line.amount_residual_currency if line.currency_id else line.amount_residual
#             else:
#                 from_currency = line.company_id.currency_id.with_context(date=line.date)
#                 line_amount = from_currency.compute(line.amount_residual, self.currency_id)
#             # For partially reconciled lines, split the residual amount
#             if line.reconcile_partial_id:
#                 partial_reconciliation_invoices = set()
#                 for pline in line.reconcile_partial_id.line_partial_ids:
#                     if pline.invoice and self.type == pline.invoice.type:
#                         partial_reconciliation_invoices.update([pline.invoice.id])
#                 line_amount = self.currency_id.round(line_amount / len(partial_reconciliation_invoices))
#                 partial_reconciliations_done.append(line.reconcile_partial_id.id)
#             self.residual += line_amount
#         print 'self.residual>>',self.residual
#         self.residual = max(self.residual, 0.0)

    _columns = {
         'amount_total': fields.float('Amount Total', help="The amount expressed in an optional other currency if it is a multi-currency entry.", digits_compute=dp.get_precision('Account')),
         'residual' :  fields.float('Residual', help="The amount expressed in an optional other currency if it is a multi-currency entry.", digits_compute=dp.get_precision('Account')),
        'paid_amount': fields.float('Paid Amount', help="The amount expressed in an optional other currency if it is a multi-currency entry.", digits_compute=dp.get_precision('Account')),     
        }
       
    def create(self, cr, uid, vals, context=None, check=True):
        account_obj = self.pool.get('account.account')
        tax_obj = self.pool.get('account.tax')
        move_obj = self.pool.get('account.move')
        cur_obj = self.pool.get('res.currency')
        journal_obj = self.pool.get('account.journal')
        context = dict(context or {})
        print 'vals> >>>', vals
        if vals.get('move_id', False):
            move = self.pool.get('account.move').browse(cr, uid, vals['move_id'], context=context)
            if move.company_id:
                vals['company_id'] = move.company_id.id
            if move.date and not vals.get('date'):
                vals['date'] = move.date
        if ('account_id' in vals) and not account_obj.read(cr, uid, [vals['account_id']], ['active'])[0]['active']:
            raise osv.except_osv(_('Bad Account!'), _('You cannot use an inactive account.'))
        if 'journal_id' in vals and vals['journal_id']:
            context['journal_id'] = vals['journal_id']
        if 'period_id' in vals and vals['period_id']:
            context['period_id'] = vals['period_id']
        if ('journal_id' not in context) and ('move_id' in vals) and vals['move_id']:
            m = move_obj.browse(cr, uid, vals['move_id'])
            context['journal_id'] = m.journal_id.id
            context['period_id'] = m.period_id.id
        # we need to treat the case where a value is given in the context for period_id as a string
        if 'period_id' in context and not isinstance(context.get('period_id', ''), (int, long)):
            period_candidate_ids = self.pool.get('account.period').name_search(cr, uid, name=context.get('period_id', ''))
            if len(period_candidate_ids) != 1:
                raise osv.except_osv(_('Error!'), _('No period found or more than one period found for the given date.'))
            context['period_id'] = period_candidate_ids[0][0]
        if not context.get('journal_id', False) and context.get('search_default_journal_id', False):
            context['journal_id'] = context.get('search_default_journal_id')
        self._update_journal_check(cr, uid, context['journal_id'], context['period_id'], context)
        move_id = vals.get('move_id', False)
        journal = journal_obj.browse(cr, uid, context['journal_id'], context=context)
        vals['journal_id'] = vals.get('journal_id') or context.get('journal_id')
        vals['period_id'] = vals.get('period_id') or context.get('period_id')
        vals['date'] = vals.get('date') or context.get('date')
        if not move_id:
            if journal.centralisation:
                # Check for centralisation
                res = self._check_moves(cr, uid, context)
                if res:
                    vals['move_id'] = res[0]
            if not vals.get('move_id', False):
                if journal.sequence_id:
                    # name = self.pool.get('ir.sequence').next_by_id(cr, uid, journal.sequence_id.id)
                    v = {
                        'date': vals.get('date', time.strftime('%Y-%m-%d')),
                        'period_id': context['period_id'],
                        'journal_id': context['journal_id']
                    }
                    if vals.get('ref', ''):
                        v.update({'ref': vals['ref']})
                    move_id = move_obj.create(cr, uid, v, context)
                    vals['move_id'] = move_id
                else:
                    raise osv.except_osv(_('No Piece Number!'), _('Cannot create an automatic sequence for this piece.\nPut a sequence in the journal definition for automatic numbering or create a sequence manually for this piece.'))
        ok = not (journal.type_control_ids or journal.account_control_ids)
        if ('account_id' in vals):
            account = account_obj.browse(cr, uid, vals['account_id'], context=context)
            if journal.type_control_ids:
                type = account.user_type
                for t in journal.type_control_ids:
                    if type.code == t.code:
                        ok = True
                        break
            if journal.account_control_ids and not ok:
                for a in journal.account_control_ids:
                    if a.id == vals['account_id']:
                        ok = True
                        break
            # Automatically convert in the account's secondary currency if there is one and
            # the provided values were not already multi-currency
            if account.currency_id and 'amount_currency' not in vals and account.currency_id.id != account.company_id.currency_id.id:
                vals['currency_id'] = account.currency_id.id
                ctx = {}
                if 'date' in vals:
                    ctx['date'] = vals['date']
                vals['amount_currency'] = cur_obj.compute(cr, uid, account.company_id.currency_id.id,
                    account.currency_id.id, vals.get('debit', 0.0) - vals.get('credit', 0.0), context=ctx)
               
        if not ok:
            raise osv.except_osv(_('Bad Account!'), _('You cannot use this general account in this journal, check the tab \'Entry Controls\' on the related journal.'))
                  
        account_invoce =  self.pool.get('account.invoice').browse(cr, uid,vals.get(move_id), context=context)                      
        for invoice in account_invoce:
            invoice_data=self.browse(cr, uid, invoice.id, context=context)
            vals['residual'] = invoice_data.residual
            vals['amount_total'] = invoice_data.amount_total
            vals['paid_amount'] =invoice_data.amount_total - invoice_data.residual    
#            
#         print 'vals>>account_move_line>>',vals['residual'] , vals['amount_total'] ,vals['paid_amount']
        result = super(account_move_line, self).create(cr, uid, vals, context=context)
        # CREATE Taxes
        if vals.get('account_tax_id', False):
            tax_id = tax_obj.browse(cr, uid, vals['account_tax_id'])
            total = vals['debit'] - vals['credit']
            base_code = 'base_code_id'
            tax_code = 'tax_code_id'
            account_id = 'account_collected_id'
            base_sign = 'base_sign'
            tax_sign = 'tax_sign'
            if journal.type in ('purchase_refund', 'sale_refund') or (journal.type in ('cash', 'bank') and total < 0):
                base_code = 'ref_base_code_id'
                tax_code = 'ref_tax_code_id'
                account_id = 'account_paid_id'
                base_sign = 'ref_base_sign'
                tax_sign = 'ref_tax_sign'
            base_adjusted = False
            for tax in tax_obj.compute_all(cr, uid, [tax_id], total, 1.00, force_excluded=False).get('taxes'):
                # create the base movement
                if base_adjusted == False:
                    base_adjusted = True
                    if tax_id.price_include:
                        total = tax['price_unit']
                    newvals = {
                        'tax_code_id': tax[base_code],
                        'tax_amount': tax[base_sign] * abs(total),
                    }
                    if tax_id.price_include:
                        if tax['price_unit'] < 0:
                            newvals['credit'] = abs(tax['price_unit'])
                        else:
                            newvals['debit'] = tax['price_unit']
                    self.write(cr, uid, [result], newvals, context=context)
                else:
                    data = {
                        'move_id': vals['move_id'],
                        'name': tools.ustr(vals['name'] or '') + ' ' + tools.ustr(tax['name'] or ''),
                        'date': vals['date'],
                        'partner_id': vals.get('partner_id', False),
                        'ref': vals.get('ref', False),
                        'statement_id': vals.get('statement_id', False),
                        'account_tax_id': False,
                        'tax_code_id': tax[base_code],
                        'tax_amount': tax[base_sign] * abs(total),
                        'account_id': vals['account_id'],
                        'credit': 0.0,
                        'debit': 0.0,
                    }
                    self.create(cr, uid, data, context)
                # create the Tax movement
                if not tax['amount'] and not tax[tax_code]:
                    continue
                data = {
                    'move_id': vals['move_id'],
                    'name': tools.ustr(vals['name'] or '') + ' ' + tools.ustr(tax['name'] or ''),
                    'date': vals['date'],
                    'partner_id': vals.get('partner_id', False),
                    'ref': vals.get('ref', False),
                    'statement_id': vals.get('statement_id', False),
                    'account_tax_id': False,
                    'tax_code_id': tax[tax_code],
                    'tax_amount': tax[tax_sign] * abs(tax['amount']),
                    'account_id': tax[account_id] or vals['account_id'],
                    'credit': tax['amount'] < 0 and -tax['amount'] or 0.0,
                    'debit': tax['amount'] > 0 and tax['amount'] or 0.0,
                }
                self.create(cr, uid, data, context)
            del vals['account_tax_id']
