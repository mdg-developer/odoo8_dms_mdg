
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
       
