from openerp import models, fields, api,exceptions, _

from openerp.exceptions import Warning as UserError

class AccountBankStatementLine(models.Model):
    _inherit ='account.bank.statement.line'
    
    account_analytic_id = fields.Many2one('account.analytic.account',
        string='Analytic Account')