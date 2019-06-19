import time
from openerp.osv import fields, osv
from openerp.tools import float_compare, float_round
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.tools import float_is_zero
from openerp.report import report_sxw

class account_bank_statement_inherit(osv.osv):

    _inherit = 'account.bank.statement'
    def button_confirm_bank(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        for st in self.browse(cr, uid, ids, context=context):
            j_type = st.journal_id.type
            if not self.check_status_condition(cr, uid, st.state, journal_type=j_type):
                continue

            self.balance_check(cr, uid, st.id, journal_type=j_type, context=context)
            if (not st.journal_id.default_credit_account_id) \
                    or (not st.journal_id.default_debit_account_id):
                raise osv.except_osv(_('Configuration Error!'), _('Please verify that an account is defined in the journal.'))
            for line in st.move_line_ids:
                if line.state != 'valid':
                    raise osv.except_osv(_('Error!'), _('The account entries lines are not in valid state.'))
            move_ids = []
            for st_line in st.line_ids:
                if not st_line.amount:
                    continue
                if st_line.account_id and not st_line.journal_entry_id.id:
                    #make an account move as before
                    vals = {
                        'debit': st_line.amount < 0 and -st_line.amount or 0.0,
                        'credit': st_line.amount > 0 and st_line.amount or 0.0,
                        'account_id': st_line.account_id.id,
                        'name': st_line.name
                    }
                    self.pool.get('account.bank.statement.line').process_reconciliation(cr, uid, st_line.id, [vals], context=context)
                elif not st_line.journal_entry_id.id:
                    raise osv.except_osv(_('Error!'), _('All the account entries lines must be processed in order to close the statement.'))
                move_ids.append(st_line.journal_entry_id.id)
            for st_line in st.expense_line_ids:
                if not st_line.amount:
                    continue
                if st_line.account_id and not st_line.journal_entry_id.id:
                    #make an account move as before
                    vals = {
                        'debit': st_line.amount < 0 and -st_line.amount or 0.0,
                        'credit': st_line.amount > 0 and st_line.amount or 0.0,
                        'account_id': st_line.account_id.id,
                        'name': st_line.name
                    }
                    self.pool.get('account.bank.statement.line').process_reconciliation(cr, uid, st_line.id, [vals], context=context)
                elif not st_line.journal_entry_id.id:
                    raise osv.except_osv(_('Error!'), _('All the account entries lines must be processed in order to close the statement.'))
                move_ids.append(st_line.journal_entry_id.id)                
            if move_ids:
                self.pool.get('account.move').post(cr, uid, move_ids, context=context)
            self.message_post(cr, uid, [st.id], body=_('Statement %s confirmed, journal items were created.') % (st.name,), context=context)
        self.link_bank_to_partner(cr, uid, ids, context=context)
        return self.write(cr, uid, ids, {'state': 'confirm', 'closing_date': time.strftime("%Y-%m-%d %H:%M:%S")}, context=context)    
    
      
    
class account_bank_statement_line(osv.osv):

    _inherit = 'account.bank.statement.line'
    _order = 'sequence'
    _columns = {
            'name': fields.text('Communication', required=True),
         #   'department_id':fields.many2one('account.department', 'Department'),
            'sequence': fields.integer('No.' , readonly=True),
            'date': fields.date('Date'),
            'account_id': fields.many2one('account.account', 'Account'),
            'income_amt': fields.float('Receive', digits_compute=dp.get_precision('Account')),
            'expense_amt': fields.float('Payment', digits_compute=dp.get_precision('Account')),
            'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account'),
            'import_fname': fields.char('Filename', size=128),
            'import_file':fields.binary('Invoice Attachment', required=False),
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
    
    
    def onchange_expense_amt(self, cr, uid, ids, expense_amt, context=None):
        val = {'amount': 0.0}
        if expense_amt:
            amount = expense_amt
            val['amount'] = -amount
        return {'value': val}   
    
    def process_reconciliation(self, cr, uid, id, mv_line_dicts, context=None):
        """ Creates a move line for each item of mv_line_dicts and for the statement line. Reconcile a new move line with its counterpart_move_line_id if specified. Finally, mark the statement line as reconciled by putting the newly created move id in the column journal_entry_id.

            :param int id: id of the bank statement line
            :param list of dicts mv_line_dicts: move lines to create. If counterpart_move_line_id is specified, reconcile with it
        """
        if context is None:
            context = {}
        st_line = self.browse(cr, uid, id, context=context)
        company_currency = st_line.journal_id.company_id.currency_id
        statement_currency = st_line.journal_id.currency or company_currency
        bs_obj = self.pool.get('account.bank.statement')
        am_obj = self.pool.get('account.move')
        aml_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')

        # Checks
        if st_line.journal_entry_id.id:
            raise osv.except_osv(_('Error!'), _('The bank statement line was already reconciled.'))
        for mv_line_dict in mv_line_dicts:
            for field in ['debit', 'credit', 'amount_currency']:
                if field not in mv_line_dict:
                    mv_line_dict[field] = 0.0
            if mv_line_dict.get('counterpart_move_line_id'):
                mv_line = aml_obj.browse(cr, uid, mv_line_dict.get('counterpart_move_line_id'), context=context)
                if mv_line.reconcile_id:
                    raise osv.except_osv(_('Error!'), _('A selected move line was already reconciled.'))

        # Create the move
        move_name = (st_line.statement_id.name or st_line.name) + "/" + str(st_line.sequence)
        move_vals = bs_obj._prepare_move(cr, uid, st_line, move_name, context=context)
        move_id = am_obj.create(cr, uid, move_vals, context=context)

        # Create the move line for the statement line
        if st_line.statement_id.currency.id != company_currency.id:
            if st_line.currency_id == company_currency:
                amount = st_line.amount_currency
            else:
                ctx = context.copy()                                                        
                ctx['active_model'] = 'account.bank.statement'
                ctx['date'] = st_line.date
                amount = currency_obj.compute(cr, uid, st_line.statement_id.currency.id, company_currency.id, st_line.amount, context=ctx)
        else:
            amount = st_line.amount
        bank_st_move_vals = bs_obj._prepare_bank_move_line(cr, uid, st_line, move_id, amount, company_currency.id, context=context)
        bnk_moveline_id = aml_obj.create(cr, uid, bank_st_move_vals, context=context)
        # Complete the dicts
        st_line_currency = st_line.currency_id or statement_currency
        st_line_currency_rate = st_line.currency_id and (st_line.amount_currency / st_line.amount) or False
        to_create = []
        bs_data = self.pool.get('account.bank.statement').browse(cr, uid, st_line.statement_id.id, context=context)
        for mv_line_dict in mv_line_dicts:
            if mv_line_dict.get('is_tax_line'):
                continue
            mv_line_dict['ref'] = move_name
            mv_line_dict['move_id'] = move_id
            mv_line_dict['period_id'] = st_line.statement_id.period_id.id
            mv_line_dict['journal_id'] = st_line.journal_id.id
            mv_line_dict['company_id'] = st_line.company_id.id
            mv_line_dict['statement_id'] = st_line.statement_id.id
            mv_line_dict['branch_id'] = bs_data.brand_id and bs_data.brand_id.id or False,
            mv_line_dict['analytic_account_id'] = st_line.analytic_account_id and st_line.analytic_account_id.id or False
            if mv_line_dict.get('counterpart_move_line_id'):
                mv_line = aml_obj.browse(cr, uid, mv_line_dict['counterpart_move_line_id'], context=context)
                mv_line_dict['partner_id'] = mv_line.partner_id.id or st_line.partner_id.id
                mv_line_dict['account_id'] = mv_line.account_id.id
            if st_line_currency.id != company_currency.id:
                ctx = context.copy()
                ctx['active_model'] = 'account.bank.statement'
                ctx['date'] = st_line.date
                mv_line_dict['amount_currency'] = mv_line_dict['debit'] - mv_line_dict['credit']
                mv_line_dict['currency_id'] = st_line_currency.id
                if st_line.currency_id and statement_currency.id == company_currency.id and st_line_currency_rate:
                    debit_at_current_rate = self.pool.get('res.currency').round(cr, uid, company_currency, mv_line_dict['debit'] / st_line_currency_rate)
                    credit_at_current_rate = self.pool.get('res.currency').round(cr, uid, company_currency, mv_line_dict['credit'] / st_line_currency_rate)
                elif st_line.currency_id and st_line_currency_rate:
                    debit_at_current_rate = currency_obj.compute(cr, uid, statement_currency.id, company_currency.id, mv_line_dict['debit'] / st_line_currency_rate, context=ctx)
                    credit_at_current_rate = currency_obj.compute(cr, uid, statement_currency.id, company_currency.id, mv_line_dict['credit'] / st_line_currency_rate, context=ctx)
                else:
                    debit_at_current_rate = currency_obj.compute(cr, uid, st_line_currency.id, company_currency.id, mv_line_dict['debit'], context=ctx)
                    credit_at_current_rate = currency_obj.compute(cr, uid, st_line_currency.id, company_currency.id, mv_line_dict['credit'], context=ctx)
                if mv_line_dict.get('counterpart_move_line_id'):
                    # post an account line that use the same currency rate than the counterpart (to balance the account) and post the difference in another line
                    ctx['date'] = mv_line.date
                    if mv_line.currency_id.id == mv_line_dict['currency_id'] \
                            and float_is_zero(abs(mv_line.amount_currency) - abs(mv_line_dict['amount_currency']), precision_rounding=mv_line.currency_id.rounding):
                        debit_at_old_rate = mv_line.credit
                        credit_at_old_rate = mv_line.debit
                    else:
                        debit_at_old_rate = currency_obj.compute(cr, uid, st_line_currency.id, company_currency.id, mv_line_dict['debit'], context=ctx)
                        credit_at_old_rate = currency_obj.compute(cr, uid, st_line_currency.id, company_currency.id, mv_line_dict['credit'], context=ctx)
                    mv_line_dict['credit'] = credit_at_old_rate
                    mv_line_dict['debit'] = debit_at_old_rate
#                     if debit_at_old_rate - debit_at_current_rate:
#                         currency_diff = debit_at_current_rate - debit_at_old_rate
#                         to_create.append(self.get_currency_rate_line(cr, uid, st_line, -currency_diff, move_id, context=context))
#                     if credit_at_old_rate - credit_at_current_rate:
#                         currency_diff = credit_at_current_rate - credit_at_old_rate
#                         to_create.append(self.get_currency_rate_line(cr, uid, st_line, currency_diff, move_id, context=context))
                    if mv_line.currency_id and mv_line_dict['currency_id'] == mv_line.currency_id.id:
                        amount_unreconciled = mv_line.amount_residual_currency
                    else:
                        amount_unreconciled = currency_obj.compute(cr, uid, company_currency.id, mv_line_dict['currency_id'] , mv_line.amount_residual, context=ctx)
                    if float_is_zero(mv_line_dict['amount_currency'] + amount_unreconciled, precision_rounding=mv_line.currency_id.rounding):
                        amount = mv_line_dict['debit'] or mv_line_dict['credit']
                        sign = -1 if mv_line_dict['debit'] else 1
                        currency_rate_difference = sign * (mv_line.amount_residual - amount)
                        if not company_currency.is_zero(currency_rate_difference):
                            exchange_lines = self._get_exchange_lines(cr, uid, st_line, mv_line, currency_rate_difference, mv_line_dict['currency_id'], move_id, context=context)
                            for exchange_line in exchange_lines:
                                to_create.append(exchange_line)

                else:
                    mv_line_dict['debit'] = debit_at_current_rate
                    mv_line_dict['credit'] = credit_at_current_rate
            elif statement_currency.id != company_currency.id:
                # statement is in foreign currency but the transaction is in company currency
                prorata_factor = (mv_line_dict['debit'] - mv_line_dict['credit']) / st_line.amount_currency
                mv_line_dict['amount_currency'] = prorata_factor * st_line.amount
            to_create.append(mv_line_dict)
        # If the reconciliation is performed in another currency than the company currency, the amounts are converted to get the right debit/credit.
        # If there is more than 1 debit and 1 credit, this can induce a rounding error, which we put in the foreign exchane gain/loss account.
        if st_line_currency.id != company_currency.id:
            diff_amount = bank_st_move_vals['debit'] - bank_st_move_vals['credit'] \
                + sum(aml['debit'] for aml in to_create) - sum(aml['credit'] for aml in to_create)
            if not company_currency.is_zero(diff_amount):                
                for bnk_id in aml_obj.browse(cr, uid, bnk_moveline_id, context=context):
                    value = {}
                    if bnk_id.debit != 0:
                        value.update({'debit':bnk_id.debit + diff_amount})
                    elif bnk_id.credit != 0:
                        value.update({'credit':bnk_id.credit + diff_amount})
                    elif bnk_id.state <> 'valid':
                        value.update({'state':'valid'}) 
                              
                    aml_obj.write(cr, uid, bnk_id.id, value, context=context)
                diff_aml = self.get_currency_rate_line(cr, uid, st_line, diff_amount, move_id, context=context)
                diff_aml['name'] = _('Rounding error from currency conversion')
                # to_create.append(diff_aml)
        # Create move lines
        move_line_pairs_to_reconcile = []
        for mv_line_dict in to_create:
            counterpart_move_line_id = None  # NB : this attribute is irrelevant for aml_obj.create() and needs to be removed from the dict
            if mv_line_dict.get('counterpart_move_line_id'):
                counterpart_move_line_id = mv_line_dict['counterpart_move_line_id']
                del mv_line_dict['counterpart_move_line_id']
            new_aml_id = aml_obj.create(cr, uid, mv_line_dict, context=context)
            if counterpart_move_line_id != None:
                move_line_pairs_to_reconcile.append([new_aml_id, counterpart_move_line_id])
        # Reconcile
        for pair in move_line_pairs_to_reconcile:
            aml_obj.reconcile_partial(cr, uid, pair, context=context)
        # Mark the statement line as reconciled
        self.write(cr, uid, id, {'journal_entry_id': move_id}, context=context) 
 
class account_bank_statement(osv.osv):

    _inherit = 'account.bank.statement'
    
    def _get_statement_from_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.bank.statement.line').browse(cr, uid, ids, context=context):
            result[line.statement_id.id] = True
        return result.keys()

    def _get_sum_entry_encoding(self, cr, uid, ids, name, arg, context=None):

        """ Find encoding total of statements "
        @param name: Names of fields.
        @param arg: User defined arguments
        @return: Dictionary of values.
        """
        res = {}
        for statement in self.browse(cr, uid, ids, context=context):
            res[statement.id] = sum((line.amount for line in statement.line_ids), 0.0) + sum((line.amount for line in statement.expense_line_ids), 0.0)
        return res    
    def _get_statement(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.bank.statement.line').browse(cr, uid, ids, context=context):
            result[line.statement_id.id] = True
        return result.keys()    
    def _end_balance(self, cursor, user, ids, name, attr, context=None):
        res = {}
        for statement in self.browse(cursor, user, ids, context=context):
            res[statement.id] = statement.balance_start
            for line in statement.line_ids:
                res[statement.id] += line.amount
            for line in statement.expense_line_ids:
                res[statement.id] += line.amount                
        return res  
    
    def _all_lines_reconciled(self, cr, uid, ids, name, args, context=None):
        res = {}
        for statement in self.browse(cr, uid, ids, context=context):
            res[statement.id] = all([line.journal_entry_id.id or line.account_id.id for line in statement.line_ids])
            res[statement.id] = all([line.journal_entry_id.id or line.account_id.id for line in statement.expense_line_ids])
        return res          
    
#     def button_confirm_bank(self, cr, uid, ids, context=None):
#         if context is None:
#             context = {}
# 
#         for st in self.browse(cr, uid, ids, context=context):
#             j_type = st.journal_id.type
#             if not self.check_status_condition(cr, uid, st.state, journal_type=j_type):
#                 continue
# 
#             self.balance_check(cr, uid, st.id, journal_type=j_type, context=context)
#             if (not st.journal_id.default_credit_account_id) \
#                     or (not st.journal_id.default_debit_account_id):
#                 raise osv.except_osv(_('Configuration Error!'), _('Please verify that an account is defined in the journal.'))
#             for line in st.move_line_ids:
#                 if line.state != 'valid':
#                     raise osv.except_osv(_('Error!'), _('The account entries lines are not in valid state.'))
#             move_ids = []
#             for st_line in st.line_ids:
#                 if not st_line.amount:
#                     continue
#                 if st_line.account_id and not st_line.journal_entry_id.id:
#                     #make an account move as before
#                     vals = {
#                         'debit': st_line.amount < 0 and -st_line.amount or 0.0,
#                         'credit': st_line.amount > 0 and st_line.amount or 0.0,
#                         'account_id': st_line.account_id.id,
#                         'name': st_line.name
#                     }
#                     self.pool.get('account.bank.statement.line').process_reconciliation(cr, uid, st_line.id, [vals], context=context)
#                 elif not st_line.journal_entry_id.id:
#                     raise osv.except_osv(_('Error!'), _('All the account entries lines must be processed in order to close the statement.'))
#                 move_ids.append(st_line.journal_entry_id.id)
#             for st_line in st.expense_line_ids:
#                 if not st_line.amount:
#                     continue
#                 if st_line.account_id and not st_line.journal_entry_id.id:
#                     #make an account move as before
#                     vals = {
#                         'debit': st_line.amount < 0 and -st_line.amount or 0.0,
#                         'credit': st_line.amount > 0 and st_line.amount or 0.0,
#                         'account_id': st_line.account_id.id,
#                         'name': st_line.name
#                     }
#                     self.pool.get('account.bank.statement.line').process_reconciliation(cr, uid, st_line.id, [vals], context=context)
#                 elif not st_line.journal_entry_id.id:
#                     raise osv.except_osv(_('Error!'), _('All the account entries lines must be processed in order to close the statement.'))
#                 move_ids.append(st_line.journal_entry_id.id)                
#             if move_ids:
#                 self.pool.get('account.move').post(cr, uid, move_ids, context=context)
#             self.message_post(cr, uid, [st.id], body=_('Statement %s confirmed, journal items were created.') % (st.name,), context=context)
#         self.link_bank_to_partner(cr, uid, ids, context=context)
#         return self.write(cr, uid, ids, {'state': 'confirm', 'closing_date': time.strftime("%Y-%m-%d %H:%M:%S")}, context=context)    
#     
    def link_bank_to_partner(self, cr, uid, ids, context=None):
        for statement in self.browse(cr, uid, ids, context=context):
            for st_line in statement.line_ids:
                if st_line.bank_account_id and st_line.partner_id and st_line.bank_account_id.partner_id.id != st_line.partner_id.id:
                    # Update the partner informations of the bank account, possibly overriding existing ones
                    bank_obj = self.pool.get('res.partner.bank')
                    bank_vals = bank_obj.onchange_partner_id(cr, uid, [st_line.bank_account_id.id], st_line.partner_id.id, context=context)['value']
                    bank_vals.update({'partner_id': st_line.partner_id.id})
                    bank_obj.write(cr, uid, [st_line.bank_account_id.id], bank_vals, context=context)   
            for st_line in statement.expense_line_ids:
                if st_line.bank_account_id and st_line.partner_id and st_line.bank_account_id.partner_id.id != st_line.partner_id.id:
                    # Update the partner informations of the bank account, possibly overriding existing ones
                    bank_obj = self.pool.get('res.partner.bank')
                    bank_vals = bank_obj.onchange_partner_id(cr, uid, [st_line.bank_account_id.id], st_line.partner_id.id, context=context)['value']
                    bank_vals.update({'partner_id': st_line.partner_id.id})
                    bank_obj.write(cr, uid, [st_line.bank_account_id.id], bank_vals, context=context)
                    
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

        return super(account_bank_statement, self).button_confirm_bank(cr, uid, ids, context=context) 
                       
    def write(self, cr, uid, ids, vals, context=None):
        res = super(account_bank_statement, self).write(cr, uid, ids, vals, context=context)
        account_bank_statement_line_obj = self.pool.get('account.bank.statement.line')
        for statement in self.browse(cr, uid, ids, context):
            for idx, line in enumerate(statement.line_ids):
                account_bank_statement_line_obj.write(cr, uid, [line.id], {'sequence': idx + 1}, context=context)
            for idx, line in enumerate(statement.expense_line_ids):
                account_bank_statement_line_obj.write(cr, uid, [line.id], {'sequence': idx + 1}, context=context)                
        return res
 
    def confirm_statement_lines(self, cr, uid, ids, context=None):
        bank_statement_line_obj = self.pool.get('account.bank.statement.line')
        for st in self.browse(cr, uid, ids, context=context):
            if st.line_ids:
                line_ids = [l.id for l in st.line_ids]
                cr.execute("UPDATE account_bank_statement_line  \
                    SET state='confirm' WHERE id in %s ",
                    (tuple(line_ids),))
                bank_statement_line_obj.invalidate_cache(cr, uid, ['state'], line_ids, context=context)
            if st.expense_line_ids:
                line_ids = [l.id for l in st.line_ids]
                cr.execute("UPDATE account_bank_statement_line  \
                    SET state='confirm' WHERE id in %s ",
                    (tuple(line_ids),))
                bank_statement_line_obj.invalidate_cache(cr, uid, ['state'], line_ids, context=context)                
        return True 
    
    def button_cancel(self, cr, uid, ids, context=None):
        bnk_st_line_ids = []
        for st in self.browse(cr, uid, ids, context=context):
            bnk_st_line_ids += [line.id for line in st.line_ids]
            bnk_st_line_ids += [line.id for line in st.expense_line_ids]
        self.pool.get('account.bank.statement.line').cancel(cr, uid, bnk_st_line_ids, context=context)
        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)
    
    def unlink(self, cr, uid, ids, context=None):
        statement_line_obj = self.pool['account.bank.statement.line']
        for item in self.browse(cr, uid, ids, context=context):
            if item.state != 'draft':
                raise osv.except_osv(
                    _('Invalid Action!'),
                    _('In order to delete a bank statement, you must first cancel it to delete related journal items.')
                )
            # Explicitly unlink bank statement lines
            # so it will check that the related journal entries have
            # been deleted first
            statement_line_obj.unlink(cr, uid, [line.id for line in item.line_ids], context=context)
            statement_line_obj.unlink(cr, uid, [line.id for line in item.expense_line_ids], context=context)
        return super(account_bank_statement, self).unlink(cr, uid, ids, context=context)                                              
    _columns = {
        'total_entry_encoding': fields.function(_get_sum_entry_encoding, string="Total Transactions",
            store={
                'account.bank.statement': (lambda self, cr, uid, ids, context=None: ids, ['line_ids', 'move_line_ids'], 10),
                'account.bank.statement.line': (_get_statement_from_line, ['amount'], 10),
            },
            help="Total of cash transaction lines."),
                'balance_end': fields.function(_end_balance,
            store = {
                'account.bank.statement': (lambda self, cr, uid, ids, c={}: ids, ['line_ids','move_line_ids','balance_start'], 10),
                'account.bank.statement.line': (_get_statement, ['amount'], 10),
            },
            string="Computed Balance", help='Balance as calculated based on Opening Balance and transaction lines'),        
                        'line_ids': fields.one2many('account.bank.statement.line',
                                    'statement_id', 'Statement lines', domain=[('income_amt', '>', 0)],
                                    states={'confirm':[('readonly', True)]}, copy=True),
                        'expense_line_ids': fields.one2many('account.bank.statement.line',
                                    'statement_id', 'Statement lines', domain=[('expense_amt', '>', 0)],
                                    states={'confirm':[('readonly', True)]}, copy=True),
                            'brand_id' :fields.many2one('res.branch', 'Branch', required=True),
                            }

        
    def _prepare_move(self, cr, uid, st_line, st_line_number, context=None):
        """Prepare the dict of values to create the move from a
           statement line. This method may be overridden to implement custom
           move generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record st_line: account.bank.statement.line record to
                  create the move from.
           :param char st_line_number: will be used as the name of the generated account move
           :return: dict of value to create() the account.move
        """
        bs_data = self.pool.get('account.bank.statement').browse(cr, uid, st_line.statement_id.id, context=context)
        return {
            'journal_id': st_line.statement_id.journal_id.id,
            'period_id': st_line.statement_id.period_id.id,
            'date': st_line.date,
            'name': st_line_number,
            'ref': st_line.ref,
            'branch_id':bs_data.brand_id and bs_data.brand_id.id or False,
        }
        
    def _prepare_move_line_vals(self, cr, uid, st_line, move_id, debit, credit, currency_id=False,
                amount_currency=False, account_id=False, partner_id=False, context=None):
        """Prepare the dict of values to create the move line from a
           statement line.

           :param browse_record st_line: account.bank.statement.line record to
                  create the move from.
           :param int/long move_id: ID of the account.move to link the move line
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
        bs_data = self.pool.get('account.bank.statement').browse(cr, uid, st_line.statement_id.id, context=context)
        return {
            'name': st_line.name,
            'date': st_line.date,
            'ref': st_line.ref,
            'move_id': move_id,
            'partner_id': par_id,
            'account_id': acc_id,
            'credit': credit,
            'debit': debit,
            'statement_id': st_line.statement_id.id,
            'journal_id': st_line.statement_id.journal_id.id,
            'period_id': st_line.statement_id.period_id.id,
            'currency_id': amount_currency and cur_id,
            'amount_currency': amount_currency,
            'branch_id': bs_data.brand_id and bs_data.brand_id.id or False,
            'analytic_account_id': st_line.analytic_account_id and st_line.analytic_account_id.id or False,
        }
