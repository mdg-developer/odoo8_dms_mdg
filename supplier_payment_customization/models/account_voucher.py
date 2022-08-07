from openerp.osv import fields, osv
from openerp.tools import float_compare
from openerp.tools.translate import _

class account_voucher(osv.osv):
    _inherit = 'account.voucher'
    
    def onchange_discount(self, cr, uid, ids, context=None):
        res = {}
        res['value'] = {'discount_account_id': False}
        return res
    
    def _check_valid_input(self, cr, uid, ids, fields, arg, context):
             
        x = {}
        data = self.browse(cr, uid, ids)[0]
        currency_obj = self.pool.get('res.currency')
        max_exchange_rate = min_exchange_rate = tolerance = 0
        if self.get_mmk_or_not(cr, uid, ids, data.currency_id.id,context=None) == False:
            
            cur_id = currency_obj.browse(cr, uid, data.currency_id.id, context=context)
            if cur_id:
                tolerance = cur_id.tolerance
            rate = self.get_rate(cr, uid, ids, data.currency_id.id, data.date, context=context)
            rate = float(format(rate, '.2f'))
            tolerance = cur_id.tolerance
            min_exchange_rate = rate - tolerance
            max_exchange_rate = rate + tolerance
            if data.voucher_rate <= max_exchange_rate and data.voucher_rate >=min_exchange_rate:
                return x
            else:               
                raise osv.except_osv(_('Please Check Rate'), _("Rate shouldn't less than Minimum Exchange Rate or Rate shouldn't greater than Maximum Exchange Rate"))
#         if data.voucher_rate:
#             if data.voucher_rate > 1:
#                 if data.voucher_rate <= data.max_exchange_rate and data.voucher_rate >=data.min_exchange_rate:
#                     return True
#                 else:               
#                    raise osv.except_osv(_('Please Check Rate'), _("Rate shouldn't less than Minimum Exchange Rate or Rate shouldn't greater than Maximum Exchange Rate"))
        return x;        
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
                        'total_discount':fields.float('Discount'),
                        'writeoff_amount': fields.function(_get_writeoff_amount, string='Difference Amount', type='float', readonly=True, help="Computed as the difference between the amount stated in the voucher and the sum of allocation on the voucher lines."),
                        'discount_account_id': fields.related('company_id', 'discount_account_id', type="many2one",
                                                               relation='account.account', required=False,
                                                               string="Discount Account",
                                                               domain="[('type', '=', 'other')]" ),
                        'voucher_rate':fields.float('Rate',default=1),
                        'exchange_rate':fields.float('Exchange Rate'),
                        'min_exchange_rate':fields.float('Minimum Exchange Rate'),
                        'max_exchange_rate':fields.float('Maximum Exchange Rate'),
                        'check_valid': fields.function(_check_valid_input, type='many2one', obj='account.invoice', string="check valid", store=True),                                                                                   
              }
    
#     def first_move_line_get(self, cr, uid, voucher_id, move_id, company_currency, current_currency, context=None):
#         '''
#         Return a dict to be use to create the first account move line of given voucher.
# 
#         :param voucher_id: Id of voucher what we are creating account_move.
#         :param move_id: Id of account move where this line will be added.
#         :param company_currency: id of currency of the company to which the voucher belong
#         :param current_currency: id of currency of the voucher
#         :return: mapping between fieldname and value of account move line to create
#         :rtype: dict
#         '''
#         voucher = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
#         debit = credit = 0.0
#         # TODO: is there any other alternative then the voucher type ??
#         # ANSWER: We can have payment and receipt "In Advance".
#         # TODO: Make this logic available.
#         # -for sale, purchase we have but for the payment and receipt we do not have as based on the bank/cash journal we can not know its payment or receipt
#         if voucher.type in ('purchase', 'payment'):
#             credit = voucher.paid_amount_in_company_currency
#         elif voucher.type in ('sale', 'receipt'):
#             debit = voucher.paid_amount_in_company_currency
#         if debit < 0: credit = -debit; debit = 0.0
#         if credit < 0: debit = -credit; credit = 0.0
#         sign = debit - credit < 0 and -1 or 1
#         #set the first line of the voucher
#         move_line = {
#                 'name': voucher.number or '/',
#                 'debit': debit,
#                 'credit': voucher.line_dr_ids.amount,
#                 'account_id': voucher.account_id.id,
#                 'move_id': move_id,
#                 'journal_id': voucher.journal_id.id,
#                 'period_id': voucher.period_id.id,
#                 'partner_id': voucher.partner_id.id,
#                 'currency_id': company_currency <> current_currency and  current_currency or False,
#                 'amount_currency': (sign * abs(voucher.amount) # amount < 0 for refunds
#                     if company_currency != current_currency else 0.0),
#                 'date': voucher.date,
#                 'date_maturity': voucher.date_due
#             }
#         return move_line
    def get_mmk_or_not(self, cr, uid, ids, currency_id,context=None):
        mmk = None
        cr.execute("""select id from res_currency where lower(name)='mmk'""")
        data = cr.fetchall()
        if data:
            mmk = data[0][0]
        if currency_id:
            if currency_id == mmk:
                return True
            else:
                return False
                        
        return True
       
    def get_rate(self, cr, uid, ids, currency_id, date, context=None):
        rate = 0.0
        cr.execute("""select rate from res_currency_rate where currency_id =%s 
        and name::date<=%s order by name desc limit 1
        """,(currency_id,date,))
        data = cr.fetchall()
        if data:
           rate = data[0][0]
        return 1/rate
    def rate_validation(self, cr, uid, ids, payment_rate_currency_id, min_exchange_rate, max_exchange_rate, voucher_rate, context=None):
        res = {}
        if voucher_rate > 1:
            if voucher_rate <= max_exchange_rate and voucher_rate >=min_exchange_rate:
                return True
            else:               
               raise osv.except_osv(_('Please Check Rate'), _("Rate shouldn't less than Minimum Exchange Rate or Rate shouldn't greater than Maximum Exchange Rate"))
           
    def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id,voucher_rate, context=None):
        if context is None:
            context = {}
        if not journal_id:
            return False
        journal_pool = self.pool.get('account.journal')
        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        
        if ttype in ('sale', 'receipt'):
            account_id = journal.default_debit_account_id
        elif ttype in ('purchase', 'payment'):
            account_id = journal.default_credit_account_id
        else:
            account_id = journal.default_credit_account_id or journal.default_debit_account_id
        tax_id = False
        if account_id and account_id.tax_ids:
            tax_id = account_id.tax_ids[0].id

        vals = {'value':{} }
        if ttype in ('sale', 'purchase'):
            vals = self.onchange_price(cr, uid, ids, line_ids, tax_id, partner_id, context)
            vals['value'].update({'tax_id':tax_id,'amount': amount})
        currency_id = False
        if journal.currency:
            currency_id = journal.currency.id
        else:
            currency_id = journal.company_id.currency_id.id
        
        #get tolerance rate
        if currency_id:
            currency_obj = self.pool.get('res.currency')
            payment_rate = 1.0
            payment_rate_currency_id = journal.currency.id or journal.company_id.currency_id.id
            if payment_rate_currency_id != currency_id:
                tmp = currency_obj.browse(cr, uid, payment_rate_currency_id, context=context).rate
                payment_rate = tmp / currency_obj.browse(cr, uid, currency_id, context=context).rate
                
                
            vals = self.onchange_payment_rate_currency(cr, uid, ids, payment_rate_currency_id, payment_rate, payment_rate_currency_id, date, amount, company_id, context=context)
            cur_id = currency_obj.browse(cr, uid, currency_id, context=context)
            if cur_id:
                tolerance = cur_id.tolerance
            rate = self.get_rate(cr, uid, ids, currency_id, date, context=context)
            rate = float(format(rate, '.2f'))
            vals['value'].update({'voucher_rate': rate})
            if rate == 0:
               vals['value'].update({'voucher_rate': 1}) 
            vals['value'].update({'payment_rate': payment_rate})
            vals['value'].update({'exchange_rate': rate})
            vals['value'].update({'min_exchange_rate': rate - tolerance})
            vals['value'].update({'max_exchange_rate': rate + tolerance})
            for key in vals.keys():
                vals[key].update(vals[key])
                    
        period_ids = self.pool['account.period'].find(cr, uid, dt=date, context=dict(context, company_id=company_id))
        vals['value'].update({
            'currency_id': currency_id,
            'payment_rate_currency_id': currency_id,
            'period_id': period_ids and period_ids[0] or False
        })
        #in case we want to register the payment directly from an invoice, it's confusing to allow to switch the journal 
        #without seeing that the amount is expressed in the journal currency, and not in the invoice currency. So to avoid
        #this common mistake, we simply reset the amount to 0 if the currency is not the invoice currency.
        if context.get('payment_expected_currency') and currency_id != context.get('payment_expected_currency'):
            second_rate = self.get_rate(cr, uid, ids, context.get('payment_expected_currency'), date, context=context)
            second_rate = float(format(second_rate, '.2f'))   
            vals['value']['amount'] = voucher_rate * amount
            amount = 0
        if partner_id:
            res = self.onchange_partner_id(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context)
            for key in res.keys():
                vals[key].update(res[key])
        return vals
                
    def onchange_date(self, cr, uid, ids, date, currency_id, payment_rate_currency_id, amount, company_id, context=None):
        """
        @param date: latest value from user input for field date
        @param args: other arguments
        @param context: context arguments, like lang, time zone
        @return: Returns a dict which contains new values, and context
        """
        if context is None:
            context ={}
        res = {'value': {}}
        tolerance = 0
        #set the period of the voucher
        period_pool = self.pool.get('account.period')
        currency_obj = self.pool.get('res.currency')
        ctx = context.copy()
        ctx.update({'company_id': company_id, 'account_period_prefer_normal': True})
        voucher_currency_id = currency_id or self.pool.get('res.company').browse(cr, uid, company_id, context=ctx).currency_id.id
        pids = period_pool.find(cr, uid, date, context=ctx)
        if pids:
            res['value'].update({'period_id':pids[0]})
        if payment_rate_currency_id:
            ctx.update({'date': date})
            payment_rate = 1.0
            if payment_rate_currency_id != currency_id:
                tmp = currency_obj.browse(cr, uid, payment_rate_currency_id, context=ctx).rate
                payment_rate = tmp / currency_obj.browse(cr, uid, voucher_currency_id, context=ctx).rate
                
                
            vals = self.onchange_payment_rate_currency(cr, uid, ids, payment_rate_currency_id, payment_rate, payment_rate_currency_id, date, amount, company_id, context=context)
            cur_id = currency_obj.browse(cr, uid, currency_id, context=ctx)
            if cur_id:
                tolerance = cur_id.tolerance
            rate = self.get_rate(cr, uid, ids, currency_id, date, context=context)
            rate = float(format(rate, '.2f'))
            vals['value'].update({'voucher_rate': rate})
            if rate == 0:
               vals['value'].update({'voucher_rate': 1}) 
            vals['value'].update({'payment_rate': payment_rate})
            vals['value'].update({'exchange_rate': rate})
            vals['value'].update({'min_exchange_rate': rate - tolerance})
            vals['value'].update({'max_exchange_rate': rate + tolerance})
            for key in vals.keys():
                res[key].update(vals[key])
        return res
    
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
#             if voucher.voucher_rate > 1:
#                 if voucher.voucher_rate <= voucher.max_exchange_rate and voucher.voucher_rate >=voucher.max_exchange_rate:
#                     print 'ok'
#                 else:
#                    raise osv.except_osv(_('Please Check Rate'), _("Rate shouldn't less than Minimum Exchange Rate or Rate shouldn't greater than Maximum Exchange Rate"))
            if voucher.voucher_rate > 1 and company_currency != current_currency: 
                credit = voucher.voucher_rate * voucher.amount
                voucher.paid_amount_in_company_currency = credit
        elif voucher.type in ('sale', 'receipt'):
            debit = voucher.paid_amount_in_company_currency
        if debit < 0: credit = -debit; debit = 0.0
        if credit < 0: debit = -credit; credit = 0.0
        sign = debit - credit < 0 and -1 or 1
        #set the first line of the voucher
        move_line = {
                'name': voucher.name or '/',
                'debit': debit,
                'credit': credit,
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
        move_ids = []
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
            
            #m3w cutomize supplier payment to get gain loss foreign curreny for partial payment
            if voucher.type in ('purchase', 'payment'):
                if not line.move_line_id:
                    raise osv.except_osv(_('Wrong voucher line'), _("The invoice you are willing to pay is not valid anymore."))
                #if len(voucher.reference) != False or len(voucher.reference) > 0:
                    
                tmp_mmk_total = tmp_fore_total = tmp_rate = v_amt = v_rate = v_total = 0.0
                tmp_mmk_total = line.move_line_id.credit
                if tmp_mmk_total <= 0:
                    tmp_mmk_total = tmp_mmk_total * -1
                tmp_fore_total = line.move_line_id.amount_currency
                if tmp_fore_total <= 0:
                    tmp_fore_total = tmp_fore_total * -1
                if tmp_fore_total == 0 or tmp_fore_total == -0:
                    tmp_fore_total = 1
                    tmp_rate = 1
                else:
                    tmp_rate =  tmp_mmk_total / tmp_fore_total        
                #tmp_rate =  tmp_mmk_total / tmp_fore_total 
                if voucher.voucher_rate > 1: 
                    v_rate = voucher.voucher_rate
                    voucher.payment_rate = voucher.voucher_rate
                else:
                    v_rate = voucher.payment_rate            
                
                if tmp_rate == 1:
                    v_total = 0
                elif tmp_rate > 1 and company_currency == current_currency:
                    fore_amt = line.amount / v_rate
                    v_total = ((tmp_rate - v_rate) * fore_amt)      
                else:            
                    v_total = ((tmp_rate - v_rate) * line.amount) 
                       
                sign = line.type == 'dr' and -1 or 1
                currency_rate_difference = sign * (v_total)    
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
                if voucher.type in ('purchase', 'payment'):
                    m_rate = (tmp_rate - v_rate)
                    if m_rate < 0:
                        move_line['debit'] = (line.amount * tmp_rate) + total_discount
                        if tmp_rate == 1 and v_rate > 1 :
                            move_line['debit'] = (amount) + total_discount
                        #tot_line += (m_rate * line.amount) * -1
                        tot_line = 0
                        #print 'tot_line>>',tot_line
                    elif m_rate > 0:
                        
                        move_line['debit'] = (line.amount * tmp_rate) + total_discount
                        #tot_line -= m_rate * line.amount
                        tot_line = 0
                        #print 'tot_line>>',tot_line   
                    if tmp_rate > 1 and company_currency == current_currency:
                        amt = (line.amount / v_rate) * tmp_rate                                                
                        move_line['debit'] = (amt) + total_discount
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
            #customize debit
            voucher_line = move_line_obj.create(cr, uid, move_line)
            rec_ids = [voucher_line, line.move_line_id.id]
 
            if not currency_obj.is_zero(cr, uid, voucher.company_id.currency_id, currency_rate_difference):
                # Change difference entry in company currency
                exch_lines = self._get_exchange_lines(cr, uid, line, move_id, currency_rate_difference, company_currency, current_currency, context=context)
                if voucher.type in ('purchase', 'payment'):
                    m_rate = (tmp_rate - v_rate)
                    if m_rate < 0:
                       #new_id = move_line_obj.create(cr, uid, exch_lines[1], context)
                       for exc in exch_lines:
                           if exc['debit'] > 0:
                               new_id = move_line_obj.create(cr, uid, exc, context)
                    elif m_rate > 0:
                        for exc in exch_lines:
                           if exc['credit'] > 0:
                               new_id = move_line_obj.create(cr, uid, exc, context)
                       #new_id = move_line_obj.create(cr, uid, exch_lines[0], context)     
                else:        
                    new_id = move_line_obj.create(cr, uid, exch_lines[0], context)
                    move_line_obj.create(cr, uid, exch_lines[1], context)
#                 new_id = move_line_obj.create(cr, uid, exch_lines[0], context)
#                 move_line_obj.create(cr, uid, exch_lines[1], context)
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
#             for rec_id in self.pool.get('account.move.line').browse(cr,uid,rec_ids,context=context):
#                 if rec_id.move_id.state== 'draft':
#                    self.pool.get('account.move').button_validate(cr,uid,rec_id.move_id.id,context=context) 
        return (tot_line, rec_lst_ids)
    
#     def onchange_line_ids(self, cr, uid, ids, line_dr_ids, line_cr_ids, amount, voucher_currency, type, partner_id, context=None):
#         context = context or {}
#         if not line_dr_ids and not line_cr_ids:
#             return {'value':{'writeoff_amount': 0.0}}
#         # resolve lists of commands into lists of dicts
#         line_dr_ids = self.resolve_2many_commands(cr, uid, 'line_dr_ids', line_dr_ids, ['amount'], context)
#         line_cr_ids = self.resolve_2many_commands(cr, uid, 'line_cr_ids', line_cr_ids, ['amount'], context)
#         #compute the field is_multi_currency that is used to hide/display options linked to secondary currency on the voucher
#         is_multi_currency = False
#         #loop on the voucher lines to see if one of these has a secondary currency. If yes, we need to see the options
#         for voucher_line in line_dr_ids+line_cr_ids:
#             line_id = voucher_line.get('id') and self.pool.get('account.voucher.line').browse(cr, uid, voucher_line['id'], context=context).move_line_id.id or voucher_line.get('move_line_id')
#             if line_id and self.pool.get('account.move.line').browse(cr, uid, line_id, context=context).currency_id:
#                 is_multi_currency = True
#                 break
#         return {'value': {'writeoff_amount': self._compute_writeoff_amount(cr, uid, line_dr_ids, line_cr_ids, amount, type), 'is_multi_currency': is_multi_currency}}
#     
account_voucher()

class account_voucher_line(osv.osv):
    _inherit = 'account.voucher.line'  
    
    
    def onchange_discount_amount(self, cr, uid, vals, total_discount, context=None):
       
        if total_discount and total_discount > 0 :
            val = {
            'total_discount': total_discount,
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
                        'total_discount':fields.float('Discount'),
                
              }
    
    def finance_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'finance_approve'}, context=None)
        return True
    
    def cashier_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'cashier_approve'}, context=None)
        return True
        
   
