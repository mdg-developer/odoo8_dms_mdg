

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from werkzeug import url_encode

class HrExpenseSheetRegisterPaymentWizard(models.TransientModel):

    _inherit = "hr.expense.sheet.register.payment.wizard"
    
    bank_statement_id = fields.Many2one(
        'account.bank.statement', string='Bank Statement',
        domain="[('journal_id',  '=', journal_id),('date',  '=', payment_date),('state','=','open')]")
    
    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id:
            # Set default payment method (we consider the first to be the default one)
            payment_methods = self.journal_id.outbound_payment_method_ids
            self.payment_method_id = payment_methods and payment_methods[0] or False
            # Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
            return {'domain': {'payment_method_id': [('payment_type', '=', 'outbound'), ('id', 'in', payment_methods.ids)]}}
        return {}

    def _get_payment_vals(self):
        """ Hook for extension """
        return {
            'partner_type': 'supplier',
            'payment_type': 'outbound',
            'partner_id': self.partner_id.id,
            'journal_id': self.journal_id.id,
            'company_id': self.company_id.id,
            'payment_method_id': self.payment_method_id.id,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'payment_date': self.payment_date,
            'communication': self.communication,
            'bank_statement_id':self.bank_statement_id.id
        }