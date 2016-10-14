from openerp.osv import fields, osv

class account_voucher(osv.osv):
    _inherit = 'account.voucher'
    
    def onchange_discount(self, cr, uid, ids, context=None):
        res = {}
        res['value'] = {'discount_account_id': False}
        return res
        
    def _get_writeoff_amount(self, cr, uid, ids, name, args, context=None):
        if not ids: return {}
        currency_obj = self.pool.get('res.currency')
        res = {}
        for voucher in self.browse(cr, uid, ids, context=context):
            print 'For Different Amt', voucher
            debit = credit = 0.0
            sign = voucher.type == 'payment' and -1 or 1
            total_discount = 0
            for l in voucher.line_dr_ids:
                print 'l', l
                debit += l.amount - l.total_discount
                print 'debit', debit
            for l in voucher.line_cr_ids:
                credit += l.amount - l.total_discount
                print 'credit', credit
                
            currency = voucher.currency_id or voucher.company_id.currency_id
            print 'currency', currency
            res[voucher.id] = currency_obj.round(cr, uid, currency, (voucher.amount - total_discount) - sign * (credit - debit))
        return res
    
    _columns = {
                        'writeoff_amount': fields.function(_get_writeoff_amount, string='Difference Amount', type='float', readonly=True, help="Computed as the difference between the amount stated in the voucher and the sum of allocation on the voucher lines."),
                        'discount_account_id': fields.related('company_id', 'discount_account_id', type="many2one",
                                                               relation='account.account', required=True,
                                                               string="Discount Account",
                                                               domain="[('type', '=', 'other')]" ),
                                                            
              }
    
    def first_move_line_get(self, cr, uid, voucher_id, move_id, company_currency, current_currency, context=None):
        '''
        Return a dict to be use to create the first account move line of given voucher.

        :param voucher_id: Id of voucher what we are creating account_move.
        :param move_id: Id of account move where this line will be added.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: mapping between fieldname and value of account move line to create
        :rtype: dict
        '''
        voucher = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        debit = credit = 0.0
        # TODO: is there any other alternative then the voucher type ??
        # ANSWER: We can have payment and receipt "In Advance".
        # TODO: Make this logic available.
        # -for sale, purchase we have but for the payment and receipt we do not have as based on the bank/cash journal we can not know its payment or receipt
        if voucher.type in ('purchase', 'payment'):
            credit = voucher.paid_amount_in_company_currency
        elif voucher.type in ('sale', 'receipt'):
            debit = voucher.paid_amount_in_company_currency
        if debit < 0: credit = -debit; debit = 0.0
        if credit < 0: debit = -credit; credit = 0.0
        sign = debit - credit < 0 and -1 or 1
        #set the first line of the voucher
        move_line = {
                'name': voucher.number or '/',
                'debit': debit,
                'credit': voucher.line_dr_ids.amount,
                'account_id': voucher.account_id.id,
                'move_id': move_id,
                'journal_id': voucher.journal_id.id,
                'period_id': voucher.period_id.id,
                'partner_id': voucher.partner_id.id,
                'currency_id': company_currency <> current_currency and  current_currency or False,
                'amount_currency': (sign * abs(voucher.amount) # amount < 0 for refunds
                    if company_currency != current_currency else 0.0),
                'date': voucher.date,
                'date_maturity': voucher.date_due
            }
        return move_line      
    def voucher_move_line_create(self, cr, uid, voucher_id, line_total, move_id, company_currency, current_currency, context=None):
        '''
        Create one account move line, on the given account move, per voucher line where amount is not 0.0.
        It returns Tuple with tot_line what is total of difference between debit and credit and
        a list of lists with ids to be reconciled with this format (total_deb_cred,list_of_lists).
 
        :param voucher_id: Voucher id what we are working with
        :param line_total: Amount of the first line, which correspond to the amount we should totally split among all voucher lines.
        :param move_id: Account move wher those lines will be joined.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: Tuple build as (remaining amount not allocated on voucher lines, list of account_move_line created in this method)
        :rtype: tuple(float, list of int)
        '''
         
        if context is None:
            context = {}
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        tot_line = line_total
        rec_lst_ids = []
        total_discount = 0.0
        total_discount_account_id = None
        total_discount_account_id = self.pool.get('account.voucher').browse(cr, uid, voucher_id, context=None).discount_account_id.id
        date = self.read(cr, uid, [voucher_id], ['date'], context=context)[0]['date']
        ctx = context.copy()
        ctx.update({'date': date})
        voucher = self.pool.get('account.voucher').browse(cr, uid, voucher_id, context=ctx)
        voucher_currency = voucher.journal_id.currency or voucher.company_id.currency_id
        ctx.update({
            'voucher_special_currency_rate': voucher_currency.rate * voucher.payment_rate ,
            'voucher_special_currency': voucher.payment_rate_currency_id and voucher.payment_rate_currency_id.id or False, })
        prec = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        print 'discount account id >>>> ', total_discount_account_id
        for line in voucher.line_ids:
            if line.total_discount > 0:
                total_discount += line.total_discount
                move_line = {
                    'journal_id': voucher.journal_id.id,
                    'period_id': voucher.period_id.id,
                    'name': line.name or '/',
                    'account_id': total_discount_account_id,
                    'move_id': move_id,
                    'partner_id': voucher.partner_id.id,
                    'currency_id': line.move_line_id and (company_currency <> line.move_line_id.currency_id.id and line.move_line_id.currency_id.id) or False,
                    'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                    'quantity': 1,
                    'credit': line.total_discount,
                    'debit':0.0,
                    'date': voucher.date
                }
                voucher_line=move_line_obj.create(cr, uid, move_line)
               # move_line = {}
               # rec_ids = [voucher_line, line.move_line_id.id]
 
            # create one move line per voucher line where amount is not 0.0
            # AND (second part of the clause) only if the original move line was not having debit = credit = 0 (which is a legal value)
            if not line.amount and not (line.move_line_id and not float_compare(line.move_line_id.debit, line.move_line_id.credit, precision_digits=prec) and not float_compare(line.move_line_id.debit, 0.0, precision_digits=prec)):
                continue
            # convert the amount set on the voucher line into the currency of the voucher's company
            # this calls res_curreny.compute() with the right context, so that it will take either the rate on the voucher if it is relevant or will use the default behaviour
            amount = self._convert_amount(cr, uid, line.untax_amount or line.amount, voucher.id, context=ctx)
            # if the amount encoded in voucher is equal to the amount unreconciled, we need to compute the
            # currency rate difference
            if line.amount == line.amount_unreconciled:
                if not line.move_line_id:
                    raise osv.except_osv(_('Wrong voucher line'), _("The invoice you are willing to pay is not valid anymore."))
                sign = line.type == 'dr' and -1 or 1
                currency_rate_difference = sign * (line.move_line_id.amount_residual - amount)
            else:
                currency_rate_difference = 0.0
            move_line = {
                'journal_id': voucher.journal_id.id,
                'period_id': voucher.period_id.id,
                'name': line.name or '/',
                'account_id': line.account_id.id,
                'move_id': move_id,
                'partner_id': voucher.partner_id.id,
                'currency_id': line.move_line_id and (company_currency <> line.move_line_id.currency_id.id and line.move_line_id.currency_id.id) or False,
                'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                'quantity': 1,
                'credit': 0.0,
                'debit': 0.0,
                'date': voucher.date
            }
            if amount < 0:
                amount = -amount
                if line.type == 'dr':
                    line.type = 'cr'
                else:
                    line.type = 'dr'
 
            if (line.type == 'dr'):
                tot_line += amount 
                move_line['debit'] = amount + total_discount
            else:
                tot_line -= amount
                move_line['credit'] = amount
 
            if voucher.tax_id and voucher.type in ('sale', 'purchase'):
                move_line.update({
                    'account_tax_id': voucher.tax_id.id,
                })
 
            # compute the amount in foreign currency
            foreign_currency_diff = 0.0
            amount_currency = False
            if line.move_line_id:
                # We want to set it on the account move line as soon as the original line had a foreign currency
                if line.move_line_id.currency_id and line.move_line_id.currency_id.id != company_currency:
                    # we compute the amount in that foreign currency.
                    if line.move_line_id.currency_id.id == current_currency:
                        # if the voucher and the voucher line share the same currency, there is no computation to do
                        sign = (move_line['debit'] - move_line['credit']) < 0 and -1 or 1
                        amount_currency = sign * (line.amount)
                    else:
                        # if the rate is specified on the voucher, it will be used thanks to the special keys in the context
                        # otherwise we use the rates of the system
                        amount_currency = currency_obj.compute(cr, uid, company_currency, line.move_line_id.currency_id.id, move_line['debit'] - move_line['credit'], context=ctx)
                if line.amount == line.amount_unreconciled:
                    foreign_currency_diff = line.move_line_id.amount_residual_currency - abs(amount_currency)
 
            move_line['amount_currency'] = amount_currency
            print 'move line >>>',move_line
            voucher_line = move_line_obj.create(cr, uid, move_line)
            rec_ids = [voucher_line, line.move_line_id.id]
 
            if not currency_obj.is_zero(cr, uid, voucher.company_id.currency_id, currency_rate_difference):
                # Change difference entry in company currency
                exch_lines = self._get_exchange_lines(cr, uid, line, move_id, currency_rate_difference, company_currency, current_currency, context=context)
                new_id = move_line_obj.create(cr, uid, exch_lines[0], context)
                move_line_obj.create(cr, uid, exch_lines[1], context)
                rec_ids.append(new_id)
 
            if line.move_line_id and line.move_line_id.currency_id and not currency_obj.is_zero(cr, uid, line.move_line_id.currency_id, foreign_currency_diff):
                # Change difference entry in voucher currency
                move_line_foreign_currency = {
                    'journal_id': line.voucher_id.journal_id.id,
                    'period_id': line.voucher_id.period_id.id,
                    'name': _('change') + ': ' + (line.name or '/'),
                    'account_id': line.account_id.id,
                    'move_id': move_id,
                    'partner_id': line.voucher_id.partner_id.id,
                    'currency_id': line.move_line_id.currency_id.id,
                    'amount_currency': (-1 if line.type == 'cr' else 1) * foreign_currency_diff,
                    'quantity': 1,
                    'credit': 0.0,
                    'debit': 0.0,
                    'date': line.voucher_id.date,
                }
                new_id = move_line_obj.create(cr, uid, move_line_foreign_currency, context=context)
                rec_ids.append(new_id)
            if line.move_line_id.id:
                rec_lst_ids.append(rec_ids)
 
            rec_ids = [voucher_line, line.move_line_id.id]
        return (tot_line, rec_lst_ids)
    
account_voucher()

class account_voucher_line(osv.osv):
    _inherit = 'account.voucher.line'
    _columns = {
                         'total_discount':fields.float('Discount'),
              }
     
    
    def onchange_discount_amount(self, cr, uid, vals, total_discount, context=None):
       
        if total_discount and total_discount > 0 :
             val = {
            'total_dis': total_discount,
            }
             return {'value': val}
     
    _columns = {
                        'state':fields.selection(
                        [('draft', 'Draft'),
                         ('cancel', 'Cancelled'),
                         ('finance_approve', 'Finance Approved'),
                         ('cashier_approve', 'Cashier Approved'),
                         ('proforma', 'Pro-forma'),
                         ('posted', 'Posted')
                        ], 'Status', readonly=True, track_visibility='onchange', copy=False,
                        help=' * The \'Draft\' status is used when a user is encoding a new and unconfirmed Voucher. \
                                    \n* The \'Pro-forma\' when voucher is in Pro-forma status,voucher does not have an voucher number. \
                                    \n* The \'Posted\' status is used when user create voucher,a voucher number is generated and voucher entries are created in account \
                                    \n* The \'Cancelled\' status is used when user cancel voucher.'),
                
              }
    
    def finance_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'finance_approve'}, context=None)
        return True
    
    def cashier_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'cashier_approve'}, context=None)
        return True
        
   
