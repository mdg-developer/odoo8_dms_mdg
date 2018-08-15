from openerp.osv import fields, osv

class AccountVoucher(osv.osv):
    _inherit ='account.voucher'    
    
    def _get_bank_statement(self, cr, uid, context=None):
        if context is None: context = {}
        invoice_pool = self.pool.get('account.invoice')
        journal_pool = self.pool.get('account.journal')
        bankstatement_pool = self.pool.get('account.bank.statement')
        if context.get('invoice_id', False):
            invoice = invoice_pool.browse(cr, uid, context['invoice_id'], context=context)
            journal_id = journal_pool.search(cr, uid, [
                ('currency', '=', invoice.currency_id.id), ('company_id', '=', invoice.company_id.id)
            ], limit=1, context=context)
            bank_statement_id =bankstatement_pool.search(cr, uid, [
                ('journal_id', '=', journal_id), ('date', '=', fields.date.context_today(self,cr,uid,context=None, timestamp=None)),('state','=','open')
            ], limit=1, context=context)
            return bank_statement_id and bank_statement_id[0] or False
        if context.get('journal_id', False):
            return context
        if not context.get('journal_id', False) and context.get('search_default_journal_id', False):
            return context
        
    _columns = {
    'bank_statement_id' : fields.many2one('account.bank.statement', 'Bank Statement'),
                }
    
    def create_bank_statement_line(self,cr,uid,voucher,move_id,name,context=None):
        bank_statement_line = self.pool.get('account.bank.statement.line')
        if voucher.bank_statement_id:
            for bankstatement_id in self.pool.get('account.bank.statement').browse(cr,uid,voucher.bank_statement_id.id):
                if bankstatement_id:
                    if voucher.type in ('purchase', 'payment'):
                        expense = voucher.amount
                        income = 0
                        amount = -1 * voucher.amount
                    elif voucher.type in ('sale', 'receipt'):
                        expense = 0
                        income = voucher.amount
                        amount = voucher.amount  
                    value = {'name':name,
                             'partner_id':voucher.partner_id.id,
                             'journal_entry_id':move_id,
                             'income_amt':income,
                             'expense_amt':expense,
                            'amount':amount,
                            'date':voucher.date,
                            'account_id':voucher.account_id.id,
                            'statement_id':bankstatement_id.id}
                    line_id = bank_statement_line.create(cr,uid,value,context=context)
                    return True
    #customize depend on sale journal principle role not odoo default            
    def action_move_line_create(self, cr, uid, ids, context=None):
        '''
        Confirm the vouchers given in ids and create the journal entries for each of them
        '''
        if context is None:
            context = {}
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        for voucher in self.browse(cr, uid, ids, context=context):
            local_context = dict(context, force_company=voucher.journal_id.company_id.id)
            if voucher.move_id:
                continue
            company_currency = self._get_company_currency(cr, uid, voucher.id, context)
            current_currency = self._get_current_currency(cr, uid, voucher.id, context)
            # we select the context to use accordingly if it's a multicurrency case or not
            context = self._sel_context(cr, uid, voucher.id, context)
            # But for the operations made by _convert_amount, we always need to give the date in the context
            ctx = context.copy()
            ctx.update({'date': voucher.date})
            # Create the account move record.
            move_id = move_pool.create(cr, uid, self.account_move_get(cr, uid, voucher.id, context=context), context=context)
            
            # Get the name of the account_move just created
            name = move_pool.browse(cr, uid, move_id, context=context).name
            # Create the first line of the voucher
            move_line_id = move_line_pool.create(cr, uid, self.first_move_line_get(cr,uid,voucher.id, move_id, company_currency, current_currency, local_context), local_context)
            move_line_brw = move_line_pool.browse(cr, uid, move_line_id, context=context)
            line_total = move_line_brw.debit - move_line_brw.credit
            rec_list_ids = []
            if voucher.type == 'sale':
                line_total = line_total - self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
            elif voucher.type == 'purchase':
                line_total = line_total + self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
            # Create one move line per voucher line where amount is not 0.0
            line_total, rec_list_ids = self.voucher_move_line_create(cr, uid, voucher.id, line_total, move_id, company_currency, current_currency, context)
            print 'line_total',line_total
            print 'rec_list_ids',rec_list_ids
            # Create the writeoff line if needed            
            ml_writeoff=None 
            if voucher:
                if voucher.reference:                    
                    if voucher.reference[:2]!='PO':          
                        ml_writeoff = self.writeoff_move_line_get(cr, uid, voucher.id, line_total, move_id, name, company_currency, current_currency, local_context)
                        print 'ml_writeoff',ml_writeoff
            if ml_writeoff:
                move_line_pool.create(cr, uid, ml_writeoff, local_context)
            # We post the voucher.
            print 'write',move_id
            self.write(cr, uid, [voucher.id], {
                'move_id': move_id,
                'state': 'posted',
                'number': name,
            })
            print 'success'
            if voucher.journal_id.entry_posted:
                move_pool.post(cr, uid, [move_id], context={})
            
            self.create_bank_statement_line(cr, uid, voucher, move_id, name, context=None)    
            # We automatically reconcile the account move lines.
            reconcile = False
            for rec_ids in rec_list_ids:
                if len(rec_ids) >= 2:
#                     if voucher.reference[:2]!='PO':
                    reconcile = move_line_pool.reconcile_partial(cr, uid, rec_ids, writeoff_acc_id=voucher.writeoff_acc_id.id, writeoff_period_id=voucher.period_id.id, writeoff_journal_id=voucher.journal_id.id)
        return True            
#     def action_move_line_create(self, cr, uid, ids, context=None):
#         '''
#         Confirm the vouchers given in ids and create the journal entries for each of them
#         '''
#         if context is None:
#             context = {}
#         move_pool = self.pool.get('account.move')
#         move_line_pool = self.pool.get('account.move.line')
#         for voucher in self.browse(cr, uid, ids, context=context):
#             local_context = dict(context, force_company=voucher.journal_id.company_id.id)
#             if voucher.move_id:
#                 continue
#             company_currency = self._get_company_currency(cr, uid, voucher.id, context)
#             current_currency = self._get_current_currency(cr, uid, voucher.id, context)
#             # we select the context to use accordingly if it's a multicurrency case or not
#             context = self._sel_context(cr, uid, voucher.id, context)
#             # But for the operations made by _convert_amount, we always need to give the date in the context
#             ctx = context.copy()
#             ctx.update({'date': voucher.date})
#             # Create the account move record.
#             move_id = move_pool.create(cr, uid, self.account_move_get(cr, uid, voucher.id, context=context), context=context)
#             self.create_bank_statement_line(cr, uid, voucher, move_id, context=None)
#             # Get the name of the account_move just created
#             name = move_pool.browse(cr, uid, move_id, context=context).name
#             # Create the first line of the voucher
#             move_line_id = move_line_pool.create(cr, uid, self.first_move_line_get(cr,uid,voucher.id, move_id, company_currency, current_currency, local_context), local_context)
#             move_line_brw = move_line_pool.browse(cr, uid, move_line_id, context=context)
#             line_total = move_line_brw.debit - move_line_brw.credit
#             rec_list_ids = []
#             if voucher.type == 'sale':
#                 line_total = line_total - self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
#             elif voucher.type == 'purchase':
#                 line_total = line_total + self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
#             # Create one move line per voucher line where amount is not 0.0
#             line_total, rec_list_ids = self.voucher_move_line_create(cr, uid, voucher.id, line_total, move_id, company_currency, current_currency, context)
# 
#             # Create the writeoff line if needed
#             ml_writeoff = self.writeoff_move_line_get(cr, uid, voucher.id, line_total, move_id, name, company_currency, current_currency, local_context)
#             if ml_writeoff:
#                 move_line_pool.create(cr, uid, ml_writeoff, local_context)
#             # We post the voucher.
#             self.write(cr, uid, [voucher.id], {
#                 'move_id': move_id,
#                 'state': 'posted',
#                 'number': name,
#             })
#             if voucher.journal_id.entry_posted:
#                 move_pool.post(cr, uid, [move_id], context={})
#             # We automatically reconcile the account move lines.
#             reconcile = False
#             for rec_ids in rec_list_ids:
#                 if len(rec_ids) >= 2:
#                     reconcile = move_line_pool.reconcile_partial(cr, uid, rec_ids, writeoff_acc_id=voucher.writeoff_acc_id.id, writeoff_period_id=voucher.period_id.id, writeoff_journal_id=voucher.journal_id.id)
#         return True
#     _defaults = {
#         'bank_statement_id': _get_bank_statement,
#         
#     }
#     @api.multi
#     def post(self):
#         """ Create the journal items for the payment and update the payment's state to 'posted'.
#             A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
#             and another in the destination reconciliable account (see _compute_destination_account_id).
#             If invoice_ids is not empty, there will be one reconciliable move line per invoice to reconcile with.
#             If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
#         """
#         for rec in self:
# 
#             if rec.state != 'draft':
#                 raise UserError(_("Only a draft payment can be posted."))
# 
#             if any(inv.state != 'open' for inv in rec.invoice_ids):
#                 raise exceptions.ValidationError(_("The payment cannot be processed because the invoice is not open!"))
# 
#             # Use the right sequence to set the name
#             if rec.payment_type == 'transfer':
#                 sequence_code = 'account.payment.transfer'
#             else:
#                 if rec.partner_type == 'customer':
#                     if rec.payment_type == 'inbound':
#                         sequence_code = 'account.payment.customer.invoice'
#                     if rec.payment_type == 'outbound':
#                         sequence_code = 'account.payment.customer.refund'
#                 if rec.partner_type == 'supplier':
#                     if rec.payment_type == 'inbound':
#                         sequence_code = 'account.payment.supplier.refund'
#                     if rec.payment_type == 'outbound':
#                         sequence_code = 'account.payment.supplier.invoice'
#             rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
#             if not rec.name and rec.payment_type != 'transfer':
#                 raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))
# 
#             # Create the journal entry
#             amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
#             move = rec._create_payment_entry(amount)
# 
#             # In case of a transfer, the first journal entry created debited the source liquidity account and credited
#             # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
#             if rec.payment_type == 'transfer':
#                 transfer_credit_aml = move.line_ids.filtered(lambda r: r.account_id == rec.company_id.transfer_account_id)
#                 transfer_debit_aml = rec._create_transfer_entry(amount)
#                 (transfer_credit_aml + transfer_debit_aml).reconcile()            
#             
#                                 
#             rec.write({'state': 'posted', 'move_name': move.name})
#             
#             if rec.bank_statement_id:
#                 for statement_id in self.env['account.bank.statement'].browse(rec.bank_statement_id.id):
#                     
#                     if statement_id:
#                         if rec.partner_type == 'customer':
#                             if rec.payment_type == 'inbound':
#                                 if amount < 0:
#                                     amount = amount * -1
#                             if rec.payment_type == 'outbound':
#                                 if amount > 0:
#                                     amount = amount * -1
#                         if rec.partner_type == 'supplier':
#                             if rec.payment_type == 'inbound':
#                                 if amount < 0:
#                                     amount = amount * -1
#                             if rec.payment_type == 'outbound':
#                                 if amount > 0:
#                                     amount = amount * -1
#                         rec.write({'ref': statement_id.name})
#                         statement_line_id =self.env['account.bank.statement.line'].create({'name':rec.communication,'amount':amount,'move_name':move.name,'partner_id':rec.partner_id.id,'date':rec.payment_date,'account_id':rec.journal_id.default_debit_account_id.id,'statement_id':statement_id.id})
#                         for line in move.line_ids:
#                             line.write({'statement_line_id':statement_line_id.id})
#                             
#         return True