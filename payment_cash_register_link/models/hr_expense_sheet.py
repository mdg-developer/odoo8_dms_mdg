from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class Hr_Expense_Sheet(models.Model):
    _inherit ='hr.expense.sheet'
    
    bank_statement_id = fields.Many2one(
        'account.bank.statement', string='Bank Statement',
        domain="[('journal_id',  '=', bank_journal_id),('date',  '=', accounting_date),('state','=','open')]")
    