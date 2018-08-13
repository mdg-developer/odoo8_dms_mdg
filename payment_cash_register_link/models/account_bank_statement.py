from openerp.osv import fields, osv
from openerp.tools import float_is_zero
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.report import report_sxw
from openerp.tools import float_compare, float_round

class AccountBankStatement(osv.osv):
    _inherit ='account.bank.statement'
    
    def _prepare_bank_move_line(self, cr, uid, st_line, move_id, amount, company_currency_id, context=None):
        """Compute the args to build the dict of values to create the counter part move line from a
           statement line by calling the _prepare_move_line_vals.

           :param browse_record st_line: account.bank.statement.line record to create the move from.
           :param int/long move_id: ID of the account.move to link the move line
           :param float amount: amount of the move line
           :param int/long company_currency_id: ID of currency of the concerned company
           :return: dict of value to create() the bank account.move.line
        """
        account_id = self._get_counter_part_account(cr, uid, st_line, context=context)
        partner_id = self._get_counter_part_partner(cr, uid, st_line, context=context)
        debit = ((amount > 0) and amount) or 0.0
        credit = ((amount < 0) and -amount) or 0.0
        cur_id = False
        amt_cur = False
        if st_line.statement_id.currency.id != company_currency_id:
            amt_cur = st_line.amount
            cur_id = st_line.statement_id.currency.id
        elif st_line.currency_id and st_line.amount_currency:
            amt_cur = st_line.amount_currency
            cur_id = st_line.currency_id.id
        return self._prepare_move_line_vals(cr, uid, st_line, move_id, debit, credit,
            amount_currency=amt_cur, currency_id=cur_id, account_id=account_id,
            partner_id=partner_id, context=context)

    def _prepare_move_line_vals(self, cr, uid, st_line, move_id, debit, credit, currency_id=False,
                amount_currency=False, account_id=False, partner_id=False, context=None):
        """Prepare the dict of values to create the move line from a
           statement line.

           :param browse_record st_line: account.bank.statement.line record to
                  create the move from.
           :param int/long move_id: ID of the account.move to link the move line
           :param float debit: debit amount of the move line
           :param float credit: credit amount of the move line
           :param int/long currency_id: ID of currency of the move line to create
           :param float amount_currency: amount of the debit/credit expressed in the currency_id
           :param int/long account_id: ID of the account to use in the move line if different
                  from the statement line account ID
           :param int/long partner_id: ID of the partner to put on the move line
           :return: dict of value to create() the account.move.line
        """
        acc_id = account_id or st_line.account_id.id
        cur_id = currency_id or st_line.statement_id.currency.id
        par_id = partner_id or (((st_line.partner_id) and st_line.partner_id.id) or False)
        return {
            'name': st_line.name,
            'date': st_line.date,
            'ref': st_line.ref,
            'move_id': move_id,
            'partner_id': par_id,
            'account_id': acc_id,
            'credit': credit,
            'debit': debit,
            'analytic_account_id': st_line.account_analytic_id.id,
            'statement_id': st_line.statement_id.id,
            'journal_id': st_line.statement_id.journal_id.id,
            'period_id': st_line.statement_id.period_id.id,
            'currency_id': amount_currency and cur_id,
            'amount_currency': amount_currency,
        }
    def button_confirm_cash(self, cr, uid, ids, context=None):
        absl_proxy = self.pool.get('account.bank.statement.line')

        TABLES = ((_('Profit'), 'profit_account_id'), (_('Loss'), 'loss_account_id'),)

        for obj in self.browse(cr, uid, ids, context=context):
            if obj.difference == 0.0:
                continue
            elif obj.difference < 0.0:
                account = obj.journal_id.loss_account_id
                name = _('Loss')
                if not obj.journal_id.loss_account_id:
                    raise osv.except_osv(_('Error!'), _('There is no Loss Account on the journal %s.') % (obj.journal_id.name,))
            else: # obj.difference > 0.0
                account = obj.journal_id.profit_account_id
                name = _('Profit')
                if not obj.journal_id.profit_account_id:
                    raise osv.except_osv(_('Error!'), _('There is no Profit Account on the journal %s.') % (obj.journal_id.name,))

            values = {
                'statement_id' : obj.id,
                'journal_id' : obj.journal_id.id,
                'account_id' : account.id,
                'amount' : obj.difference,
                'name' : name,
            }
            absl_proxy.create(cr, uid, values, context=context)

        return super(AccountBankStatement, self).button_confirm_bank(cr, uid, ids, context=context)
