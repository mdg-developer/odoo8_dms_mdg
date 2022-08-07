import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp

class account_invoice(models.Model):
    _inherit = "account.invoice"
    
    journal_claim = fields.Boolean(default=False)
    due_date_rate = fields.Float(string='Due Date MMK Rate',default=0)
    #due_date_rate = fields.float
    def account_journal_get(self,invoice):       
        
        journal_id = self.env['account.journal'].search([('code', '=', 'MISC')])[0]
        move = {
            'name': '/',
            'journal_id': journal_id.id,
            
            'date': invoice.date_invoice,
            'ref': invoice.number,
            'period_id': invoice.period_id.id,
        }
        return move
    
    def first_move_line_get_ap_ar(self,invoice, move_id,journal_id,debit,credit,amount,account_id, company_currency, current_currency):
        
        
        
        sign = debit - credit < 0 and -1 or 1
        move_line = {
                'name': invoice.name or '/',
                'debit': debit,
                'credit': credit,
                'account_id': account_id,
                'move_id': move_id.id,
                'journal_id': journal_id,
                'period_id': invoice.period_id.id,
                'partner_id': invoice.partner_id.id,
                'currency_id': False,#company_currency <> current_currency and  current_currency or False,
                'amount_currency':False,#(sign * abs(amount)  # amount < 0 for refunds
                    #if company_currency != current_currency else 0.0),
                'date': invoice.date_invoice,
                'date_maturity': invoice.date_due
            }
        return move_line
    
    
        
    @api.multi
    def claim_journal(self):
        
        account_move = self.env['account.move']
        account_move_line = self.env['account.move.line'] 
        due_rate = agree_rate = 0       
        for inv in self:
            if inv.type == 'in_invoice' and inv.currency_id.name != 'MMK' and inv.journal_claim != True:
                inv.write({'journal_claim':True})
                total_price = amount_currency = 0
                journal_id = self.env['account.journal'].search([('code', '=', 'MISC')])[0]
                due_rate = self.due_date_rate
                agree_rate = self.get_purchase_agree_rate()
                if agree_rate > 0:
                    total_price = (agree_rate - due_rate) * self.amount_total
                    amount_currency = (agree_rate - due_rate)
                #for line in self.invoice_line:
                    
                if total_price != 0:
                    move_id = account_move.create(self.account_journal_get(inv))
                    if total_price > 0:
                        account_move_line.create(self.first_move_line_get_ap_ar(inv, move_id,journal_id.id, total_price,0,amount_currency, inv.partner_id.loss_account_id.id, inv.journal_id.company_id.currency_id.id, inv.currency_id.id))
                        account_move_line.create(self.first_move_line_get_ap_ar(inv, move_id,journal_id.id, 0,total_price,amount_currency, inv.partner_id.property_account_receivable.id, inv.journal_id.company_id.currency_id.id, inv.currency_id.id))
                                                
                    else:
                        total_price = total_price * -1
                        account_move_line.create(self.first_move_line_get_ap_ar(inv, move_id,journal_id.id, 0, total_price,amount_currency, inv.partner_id.gain_account_id.id, inv.journal_id.company_id.currency_id.id, inv.currency_id.id))
                        account_move_line.create(self.first_move_line_get_ap_ar(inv, move_id,journal_id.id, total_price,0,amount_currency, inv.partner_id.property_account_receivable.id, inv.journal_id.company_id.currency_id.id, inv.currency_id.id))            
#                     if total_price > 0:
#                         account_move_line.create(self.first_move_line_get_ap_ar(inv, move_id,journal_id.id, 0, total_price,amount_currency, inv.partner_id.gain_account_id.id, inv.journal_id.company_id.currency_id.id, inv.currency_id.id))
#                         account_move_line.create(self.first_move_line_get_ap_ar(inv, move_id,journal_id.id, total_price,0,amount_currency, inv.partner_id.property_account_receivable.id, inv.journal_id.company_id.currency_id.id, inv.currency_id.id))
#                     else:
#                         total_price = total_price * -1
#                         account_move_line.create(self.first_move_line_get_ap_ar(inv, move_id,journal_id.id, total_price,0,amount_currency, inv.partner_id.loss_account_id.id, inv.journal_id.company_id.currency_id.id, inv.currency_id.id))
#                         account_move_line.create(self.first_move_line_get_ap_ar(inv, move_id,journal_id.id, 0,total_price,amount_currency, inv.partner_id.property_account_receivable.id, inv.journal_id.company_id.currency_id.id, inv.currency_id.id))            
                        
