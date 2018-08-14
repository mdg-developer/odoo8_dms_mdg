import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp

# mapping invoice type to journal type
TYPE2JOURNAL = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale_refund',
    'in_refund': 'purchase_refund',
}

# mapping invoice type to refund type
TYPE2REFUND = {
    'out_invoice': 'out_refund',        # Customer Invoice
    'in_invoice': 'in_refund',          # Supplier Invoice
    'out_refund': 'out_invoice',        # Customer Refund
    'in_refund': 'in_invoice',          # Supplier Refund
}

MAGIC_COLUMNS = ('id', 'create_uid', 'create_date', 'write_uid', 'write_date')

class account_invoice(models.Model):
    _inherit = "account.invoice"

    def line_get_convert(self, line, part, date):
        if line is not None:

            debit = round(line['debit'], 1)
            credit = round(line['credit'], 1)
            price = debit + (credit * -1),
#             price = debit+ credit,
            print ' lineeeeeeeeeeeee',line
            
            return {
                'date_maturity': line.get('date_maturity', False),
                'partner_id': part,
                'name': line['name'][:64],
                'date': date,
                'debit': line['debit'],  # line['price']>0 and line['price'],
                'credit':  line['credit'],  # line['price']<0 and -line['price'],
                'account_id': line['account_id'],
                # 'account_id': account_id,
                'analytic_lines': line.get('analytic_lines', []),
                'amount_currency': price[0] > 0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
                'currency_id': line.get('currency_id', False),
                'tax_code_id': line.get('tax_code_id', False),
                'tax_amount': line.get('tax_amount', False),
                'ref': line.get('ref', False),
                'quantity': line.get('quantity', 1.00),
                'product_id': line.get('product_id', False),
                'product_uom_id': line.get('uos_id', False),
                'analytic_account_id': line.get('analytic_account_id', False),
            }
            
    @api.model
    def move_line_get_item(self, line):
        return {
            'type': 'src',
            'name': line.name.split('\n')[0][:64],
            'price_unit': line.price_unit,
            'quantity': line.quantity,
            'price': line.price_subtotal+line.discount_amt,
            'account_id': line.account_id.id,
            'product_id': line.product_id.id,
            'uos_id': line.uos_id.id,
            'account_analytic_id': line.account_analytic_id.id,
            'taxes': line.invoice_line_tax_id,
            'foc':line.foc,
        }   

    @api.model
    def move_line_get(self,invoice_id):
        inv = self.env['account.invoice'].browse(invoice_id)
        currency = inv.currency_id.with_context(date=inv.date_invoice)
        company_currency = inv.company_id.currency_id
        discount_account_id=discount_cash_account_id=None
        
        dis_per=dis_amt=deduct_amt=total=additional_discount=0.0
        discount_cash_account_id=inv.invoice_line[0].product_id.product_tmpl_id.main_group.property_account_discount.id
        discount_account_id=inv.company_id.discount_account_id.id
        if discount_cash_account_id and discount_account_id==None:
            raise orm.except_orm(_('Error :'), _("Please select the Discount code and Cash Discount Code in Sale setting!"))
        res = []
        deduct_amt=inv.deduct_amt
        additional_discount=(inv.amount_untaxed * (inv.additional_discount/100))
        discount_total=inv.discount_total
        ref=inv.origin
        for line in inv.invoice_line:
            
            mres = self.move_line_get_item(line)
            mres['ref']=ref
            mres['is_discount']=False
            product = self.env['product.product'].browse(mres.get('product_id', False))
            print 'mres',mres,ref,product.default_code
            if not mres:
                continue
            res.append(mres)
            tax_code_found = False
            taxes = line.invoice_line_tax_id.compute_all(
                (line.price_unit * (1.0 - (line.discount or 0.0) / 100.0)),
                line.quantity, line.product_id, inv.partner_id)['taxes']
            for tax in taxes:
                if inv.type in ('out_invoice', 'in_invoice'):
                    tax_code_id = tax['base_code_id']
                    tax_amount = line.price_subtotal * tax['base_sign']
                else:
                    tax_code_id = tax['ref_base_code_id']
                    tax_amount = line.price_subtotal * tax['ref_base_sign']

                if tax_code_found:
                    if not tax_code_id:
                        continue
                    res.append(dict(mres))
                    res[-1]['price'] = 0.0
                    res[-1]['account_analytic_id'] = False
                elif not tax_code_id:
                    continue
                tax_code_found = True

                res[-1]['tax_code_id'] = tax_code_id
                res[-1]['tax_amount'] = currency.compute(tax_amount, company_currency)
            if line.net_total <0:
                val1={'type': 'src',
                        'name': line.product_id.name_template,
                        'price_unit':line.net_total,
                        'quantity': 1,
                        'price':line.net_total,
                        'account_id': discount_account_id,
                        'product_id':  line.product_id.id,
                        'is_discount':True,
                        'ref':ref,
                         'foc':False,
                        'account_analytic_id': inv.invoice_line[0].account_analytic_id.id,
                        'taxes': False,
                        }
                res.append(val1)                
            total=line.discount_amt

            val1={'type': 'src',
                    'name': line.product_id.name_template,
                    'price_unit': total,
                    'quantity': 1,
                    'price':-1* total,
                    'account_id': discount_account_id,
                    'product_id':  line.product_id.id,
                    'is_discount':True,
                    'ref':ref,
                     'foc':False,
                    'account_analytic_id': inv.invoice_line[0].account_analytic_id.id,
                    'taxes': False,
                    }
            if total>0:
                res.append(val1)
        if deduct_amt+additional_discount>0:
                val2={'type': 'src',
                            'name': 'Sale Discount',
                            'price_unit': deduct_amt+additional_discount,
                            'quantity': 1,
                            'price':1*(deduct_amt+additional_discount),
                            'account_id': discount_cash_account_id,
                            'product_id': False,
                            'ref':ref,
                            'is_discount':True,
                             'foc':False,
                            'account_analytic_id': inv.invoice_line[0].account_analytic_id.id,
                            'taxes': False,
                            }
                res.append(val2)

        return res
        print 'resssssssssssssssssss',res


    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_invoice_tax = self.env['account.invoice.tax']
        account_move = self.env['account.move']
        analytic_row=''
        for inv in self:
            if not inv.journal_id.sequence_id:
                raise except_orm(_('Error!'), _('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line:
                raise except_orm(_('No Invoice Lines!'), _('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)
            company_currency = inv.company_id.currency_id
            if not inv.date_invoice:
                # FORWARD-PORT UP TO SAAS-6
                if inv.currency_id != company_currency and inv.tax_line:
                    raise except_orm(
                        _('Warning!'),
                        _('No invoice date!'
                            '\nThe invoice currency is not the same than the company currency.'
                            ' An invoice date is required to determine the exchange rate to apply. Do not forget to update the taxes!'
                        )
                    )                
                inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            date_invoice = inv.date_invoice

            # create the analytical lines, one move line per invoice line
            iml = inv._get_analytic_lines()
            for line in iml:
                analytic_row = line.get('account_analytic_id')
            # check if taxes are all computed
            compute_taxes = account_invoice_tax.compute(inv.with_context(lang=inv.partner_id.lang))  
            tax_value = tax_amount_currency = 0.0  
            for i, t in compute_taxes.items():                                              
                tax_value += t.get('tax_amount') 
                tax_amount_currency += t.get('amount')
                           
            inv.check_tax_lines(compute_taxes)
            
            # I disabled the check_total feature
            if self.env.user.has_group('account.group_supplier_inv_check_total'):
                if inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding / 2.0):
                    raise except_orm(_('Bad Total!'), _('Please verify the price of the invoice!\nThe encoded total does not match the computed total.'))

            if inv.payment_term:
                total_fixed = total_percent = 0
                for line in inv.payment_term.line_ids:
                    if line.value == 'fixed':
                        total_fixed += line.value_amount
                    if line.value == 'procent':
                        total_percent += line.value_amount
                total_fixed = (total_fixed * 100) / (inv.amount_total or 1.0)
                if (total_fixed + total_percent) > 100:
                    raise except_orm(_('Error!'), _("Cannot create the invoice.\nThe related payment term is probably misconfigured as it gives a computed amount greater than the total invoiced amount. In order to avoid rounding issues, the latest line of your payment term must be of type 'balance'."))

            # one move line per tax line
            iml += account_invoice_tax.move_line_get(inv.id)
                        
            if inv.type in ('in_invoice', 'in_refund'):
                ref = inv.reference
            else:
                ref = inv.number

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, ref, iml)

            name = inv.supplier_invoice_number or inv.name or '/'
            totlines = []
            if inv.payment_term:
                totlines = inv.with_context(ctx).payment_term.compute(total, date_invoice)[0]                
            if totlines:
                res_amount_currency = total_currency
                ctx['date'] = date_invoice
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency                                           
                    
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'ref': ref,
                        'is_discount':False,
                        'analytic_account_id': analytic_row, 
                    })
            else:
                
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'ref': ref,
                 'is_discount':False,
                 'analytic_account_id': analytic_row, 

                })

            date = date_invoice

            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)

            # line = [(0, 0, self.line_get_convert(l, part.id, date)) for l in iml]
            data = []
            for res in iml:
                res['ref'] = inv.origin
                data.append(res)
            iml = data
            line_cr = [self.line_get_convert_new(l, part.id, date) for l in iml]
            line_tmp = [self.line_get_convert_dr(l, part.id, date, tax_value, tax_amount_currency) for l in iml]
            line_dr = self.line_dr_convert_account_with_principle(line_tmp)
            # line_product = [self.line_get_product(l, part.id, date) for l in iml]
            # line_dr = [(0, 0, self.line_get_convert_accountid(l, part.id, date)) for l in line_cr]
            lines = line_cr + line_dr
            line = [(0, 0, self.line_get_convert(l, part.id, date)) for l in lines  if l is not None]
            
            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            if journal.centralisation:
                raise except_orm(_('User Error!'),
                        _('You cannot create an invoice on a centralized journal. Uncheck the centralized counterpart box in the related journal from the configuration menu.'))

            line = inv.finalize_invoice_move_lines(line)

            move_vals = {
                'ref': inv.reference or inv.name,
                'line_id': line,
                'journal_id': journal.id,
                'date': inv.date_invoice,
                'narration': inv.comment,
                'company_id': inv.company_id.id,
            }
            ctx['company_id'] = inv.company_id.id
            period = inv.period_id
            if not period:
                period = period.with_context(ctx).find(date_invoice)[:1]
            if period:
                move_vals['period_id'] = period.id
                for i in line:
                    i[2]['period_id'] = period.id

            ctx['invoice'] = inv
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            print 'move_valsmove_valsmove_vals', move_vals
            move = account_move.with_context(ctx_nolang).create(move_vals)            
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'period_id': period.id,
                'move_name': move.name,
                'analytic_account_id': analytic_row, 
            }
            inv.with_context(ctx).write(vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
        self._log_event()
        return True

    @api.model
    def _prepare_refund(self, invoice, date=None, period_id=None, description=None, journal_id=None):
        """ Prepare the dict of values to create the new refund from the invoice.
            This method may be overridden to implement custom
            refund generation (making sure to call super() to establish
            a clean extension chain).

            :param record invoice: invoice to refund
            :param string date: refund creation date from the wizard
            :param integer period_id: force account.period from the wizard
            :param string description: description of the refund from the wizard
            :param integer journal_id: account.journal from the wizard
            :return: dict of value to create() the refund
        """
        values = {}
        product_obj = self.pool.get('product.product')
        for field in ['name', 'reference', 'comment', 'date_due', 'partner_id', 'company_id',
                'account_id', 'currency_id', 'payment_term', 'user_id', 'fiscal_position']:
            if invoice._fields[field].type == 'many2one':
                values[field] = invoice[field].id
            else:
                values[field] = invoice[field] or False
        values['invoice_line'] = self._refund_cleanup_lines(invoice.invoice_line)
        if journal_id:
            journal = self.env['account.journal'].browse(journal_id)
            if journal:
                    j_name=journal.name.strip()
        if j_name =='Sale Return Journal':
            for line in values['invoice_line']:
                pp_ids = self.env['product.product'].browse(line[2]['product_id'])
                if pp_ids.categ_id.property_sale_return_account_id.id:
                    line[2]['account_id']=pp_ids.categ_id.property_sale_return_account_id.id    
                else:
                    raise except_orm(_('Sale Return Account Error!'),
                                        _('Product %s has no related Sale Return Account.') % (pp_ids.name))      
        tax_lines = filter(lambda l: l.manual, invoice.tax_line)
        values['tax_line'] = self._refund_cleanup_lines(tax_lines)

        if journal_id:
            journal = self.env['account.journal'].browse(journal_id)
        elif invoice['type'] == 'in_invoice':
            journal = self.env['account.journal'].search([('type', '=', 'purchase_refund')], limit=1)
        else:
            journal = self.env['account.journal'].search([('type', '=', 'sale_refund')], limit=1)
        values['journal_id'] = journal.id

        values['type'] = TYPE2REFUND[invoice['type']]
        values['date_invoice'] = date or fields.Date.context_today(invoice)
        values['state'] = 'draft'
        values['number'] = False
        values['origin'] = invoice.number

        if period_id:
            values['period_id'] = period_id
        if description:
            values['name'] = description
        return values