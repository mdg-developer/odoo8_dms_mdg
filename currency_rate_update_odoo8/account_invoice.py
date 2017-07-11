import itertools
from lxml import etree
from openerp.osv import fields, osv
from datetime import datetime
from openerp.exceptions import except_orm, Warning, RedirectWarning
import openerp.addons.decimal_precision as dp
from openerp import models, api, _


class account_invoice(osv.osv):

    _inherit = 'account.invoice'
    _columns = {
    
        'entry_date':fields.date('Entry Date'),
        }
    _defaults = {
        'entry_date':datetime.today(),
    }
    
    @api.model
    def line_get_convert_rate(self, line,rate,currencey_rate, part, date):
        if rate==0:
            rate=1.0
        #print 'Line Price',line['amount_currency']
        
        return {
            'date_maturity': line.get('date_maturity', False),
            'partner_id': part,
            'name': line['name'][:64],
            'date': date,
            'date_maturity':date,
            'credit': (line['price'] *currencey_rate)>0 and line['price']*currencey_rate,
            'debit': (line['price']*currencey_rate)<0 and -line['price']*currencey_rate,
            'account_id': line['account_id'],
            'analytic_lines': line.get('analytic_lines', []),
        #    'amount_currency': line['price']>0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
            'amount_currency':  line['price'],
            'currency_id': line.get('currency_id', False),
            'tax_code_id': line.get('tax_code_id', False),
            'tax_amount': line.get('tax_amount', False),
            'ref': line.get('ref', False),
            'quantity': line.get('quantity',1.00),
            'product_id': line.get('product_id', False),
            'product_uom_id': line.get('uos_id', False),
            'analytic_account_id': line.get('account_analytic_id', False),
            'currency_rate': currencey_rate,
            #'currency_rate': line.get('currencey_rate', False),
        } 
         
    def line_get_convert_rate_base_currency(self, line, part, date):
        
        return {
            'date_maturity': line.get('date_maturity', False),
            'partner_id': part,
            'name': line['name'][:64],
            'date': date,
            'credit': line['price']>0 and line['price'],
            'debit': line['price']<0 and -line['price'],
            'account_id': line['account_id'],
            'analytic_lines': line.get('analytic_lines', []),
            'amount_currency': line['price']>0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
            'currency_id': line.get('currency_id', False),
            'tax_code_id': line.get('tax_code_id', False),
            'tax_amount': line.get('tax_amount', False),
            'ref': line.get('ref', False),
            'quantity': line.get('quantity',1.00),
            'product_id': line.get('product_id', False),
            'product_uom_id': line.get('uos_id', False),
            'analytic_account_id': line.get('account_analytic_id', False),
          
        }   
    def get_currency_rate(self,cr,uid,currency_id,context=None):
        currency_rate_obj=self.pool.get('res.currency.rate')
        val=0.0
        val1=None
        rate=0.0
        rate1=None
        if currency_id:
            
            rate_id=currency_rate_obj.search(cr, uid, [
                    ('currency_id', '=', currency_id)], limit=1, order='name DESC')
            
            if rate_id:
                #currencyRate
                val1=currency_rate_obj.read(cr,uid,rate_id,{'multi_rate'},context=context)
                if val1:
                    val=val1[0]['multi_rate']
                #Rate  
                rate1=currency_rate_obj.read(cr,uid,rate_id,{'rate'},context=context)
                if rate1:
                    rate=rate1[0]['rate']
            
                
        return val ,rate 
    
    @api.multi    
    def compute_invoice_totals(self, company_currency, ref, invoice_move_lines):
    
        total = 0
        total_currency = 0
        price_unit=0.0
           
                
        for line in invoice_move_lines:
            #print 'Line price Value', line['price']
            if self.currency_id != company_currency:
                currency = self.currency_id.with_context(date=self.date_invoice or datetime.today())
                line['currency_id'] = currency.id
                line['amount_currency'] = False
                #line['price'] = currency.compute(line['price'], company_currency)
                line['price'] = line['price'] 
                #print 'Ok'
            else: 
                #Base Currency
                line['currency_id'] = False
                line['amount_currency'] = False
                line['price'] = - line['price']
                #print 'Hello'
            line['ref'] = ref
            if self.type in ('out_invoice','in_refund'):
                total += line['price']
                #total = line['price']
                total_currency += line['amount_currency'] or line['price']
                line['price'] = - line['price']
               # line['price'] = -1500
                #print 'True'
            else:
                #Base Currency
                total -= line['price']
                total_currency -= line['amount_currency'] or line['price']
                #print 'Wrong'
        return total, total_currency, invoice_move_lines
    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_invoice_tax = self.env['account.invoice.tax']
        account_move = self.env['account.move']

        for inv in self:
            if not inv.journal_id.sequence_id:
                raise except_orm(_('Error!'), _('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line:
                raise except_orm(_('No Invoice Lines!'), _('Please create some invoice lines.'))
            
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)
           
            if not inv.date_invoice:
                #self.write({'date_invoice':datetime.today()})
                inv.with_context(ctx).write({'date_invoice': datetime.today()})
            date_invoice = inv.date_invoice

            company_currency = inv.company_id.currency_id
            # create the analytical lines, one move line per invoice line
            iml = inv._get_analytic_lines()
          
            # check if taxes are all computed
          #  compute_taxes = account_invoice_tax.compute(inv)
            compute_taxes = account_invoice_tax.compute(inv.with_context(lang=inv.partner_id.lang))
            inv.check_tax_lines(compute_taxes)

            # I disabled the check_total feature
            group_check_total = self.env.ref('account.group_supplier_inv_check_total')
            if self.env.user in group_check_total.users:
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
            #    ref = self._convert_ref(inv.number)
                ref = inv.number

            diff_currency = inv.currency_id != company_currency
            currency_rate,rate = self.get_currency_rate(inv.currency_id.id)
            
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, ref, iml)
            #print 'Move Line for the total',total
            #print 'Move Line for the total_currency',total_currency
            name = inv.name or inv.supplier_invoice_number or '/'
            #print 'name',name
            totlines = []
            price_unit=0.0
            for val in iml:
                price_unit=val['price_unit']
        
            
            if inv.payment_term:
                totlines = inv.with_context(ctx).payment_term.compute(total, date_invoice)[0]
            if totlines:
                #print 'if state'
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
                    ##print 'inv.line.account_analytic_id.id',inv.invoice_line[0].account_analytic_id.id
                   
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                       # 'price': price_unit,
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'ref': ref,
                        'account_analytic_id': inv.invoice_line[0].account_analytic_id.id,

                    })
            else:
                #print 'else state'
               
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    #'price': price_unit,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'ref': ref,
                   'account_analytic_id': inv.invoice_line[0].account_analytic_id.id,

                })

            date = date_invoice
            #print 'date',date
            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            #print 'part',part
           # line = [(0, 0, self.line_get_convert_rate(l, currency_rate, part.id, date)) for l in iml]
            if (inv.currency_id.id==120):
                
                line = [(0, 0, self.line_get_convert_rate_base_currency(l,  part.id, date)) for l in iml]
            else:
                line = [(0, 0, self.line_get_convert_rate(l,rate,currency_rate, part.id, date)) for l in iml]
            line = inv.group_lines(iml, line)
            #print 'line',line
            journal = inv.journal_id.with_context(ctx)
            if journal.centralisation:
                raise except_orm(_('User Error!'),
                        _('You cannot create an invoice on a centralized journal. Uncheck the centralized counterpart box in the related journal from the configuration menu.'))

            line = inv.finalize_invoice_move_lines(line)

            move_vals = {
                'ref': inv.reference or inv.name,
                'line_id': line,
                'journal_id': journal.id,
                'date': date,
                'narration': inv.comment,
                'company_id': inv.company_id.id,
            }
            #print 'move_vals',move_vals
            ctx['company_id'] = inv.company_id.id
            period = inv.period_id
            if not period:
                period = period.with_context(ctx).find(date_invoice)[:1]
            if period:
                move_vals['period_id'] = period.id
                for i in line:
                    i[2]['period_id'] = period.id

            ctx['invoice'] = inv
            move = account_move.with_context(ctx).create(move_vals)
            #print 'create move',move
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'period_id': period.id,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
            #print 'after updating ',inv.with_context(ctx).write(vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
            print 'post',move.post()
        self._log_event()
        return True    

    
    
    
