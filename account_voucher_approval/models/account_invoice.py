import itertools
from lxml import etree
from openerp.osv import fields, osv
from openerp import models, fields, api, _
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
from openerp.exceptions import except_orm, Warning, RedirectWarning

# mapping invoice type to journal type
TYPE2JOURNAL = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale_refund',
    'in_refund': 'purchase_refund',
}
class account_invoice(models.Model):
    _inherit = "account.invoice"

    def create(self, cr, uid, vals, context=None):
        obj_sequence = self.pool.get('ir.sequence')
        """Update the registry when a new rule is created."""
        if vals.get('partner_id'):
                partner_id=vals['partner_id']
                part = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)    
                defaults=self.onchange_partner_id(cr, uid, [], 'out_invoice', partner_id)['value']
                vals = dict(defaults, **vals)
        cr.execute(" select af.id from account_period ap ,account_fiscalyear af where ap.fiscalyear_id=af.id and ap.date_start <=current_date and ap.date_stop >=current_date")
        fiscalyear_id=cr.fetchone()[0]
        c = {'fiscalyear_id': fiscalyear_id}
        cr.execute("select id from ir_sequence where name='Sales Journal'  and prefix like '%INV%' ")
        sequence=cr.fetchone()[0]
        if sequence:      
            new_name = obj_sequence.next_by_id(cr, uid, sequence , c)
        vals['number'] = new_name
        vals['internal_number'] = new_name                
        res_id = super(account_invoice, self).create(
            cr, uid, vals, context=context)
        cr.execute("update account_invoice set number=%s where id =%s",(new_name,res_id,))
        return res_id
        
    def write(self, cursor, user, ids, vals, context=None):
        """
        Serialise before Write
        @param cursor: Database Cursor
        @param user: ID of User
        @param  ids: ID of current record.
        @param vals: Values of current record.
        @param context: Context(no direct use).
        """
        # Validate before save
        if type(ids) in [list, tuple] and ids:
            ids = ids[0]
            if vals.get('partner_id'):
                partner_id=vals['partner_id']
                part = self.pool.get('res.partner').browse(cursor, user, partner_id, context=context)    
                defaults=self.onchange_partner_id(cursor, user, [], 'out_invoice', partner_id)['value']
                vals = dict(defaults, **vals)
        ctx = dict(context or {}, mail_create_nolog=True)
        new_id = super(account_invoice, self).write(cursor, user, ids, vals, context=context)
        return new_id        
    @api.multi    
    def onchange_partner_id(self, type, partner_id, date_invoice=False,
            payment_term=False, partner_bank_id=False, company_id=False):
        account_id = False
        payment_term_id = False
        fiscal_position = False
        bank_id = False
        code=False
        street= False
        street2=False
        city=False
        state_id=  False
        country_id=False
        township=False
        pricelist=False
        payment_type='cash'
        if partner_id:
            p = self.env['res.partner'].browse(partner_id)
            rec_account = p.property_account_receivable
            pay_account = p.property_account_payable

            if company_id:
                if p.property_account_receivable.company_id and \
                        p.property_account_receivable.company_id.id != company_id and \
                        p.property_account_payable.company_id and \
                        p.property_account_payable.company_id.id != company_id:
                    prop = self.env['ir.property']
                    rec_dom = [('name', '=', 'property_account_receivable'), ('company_id', '=', company_id)]
                    pay_dom = [('name', '=', 'property_account_payable'), ('company_id', '=', company_id)]
                    res_dom = [('res_id', '=', 'res.partner,%s' % partner_id)]
                    rec_prop = prop.search(rec_dom + res_dom) or prop.search(rec_dom)
                    pay_prop = prop.search(pay_dom + res_dom) or prop.search(pay_dom)
                    rec_account = rec_prop.get_by_record(rec_prop)
                    pay_account = pay_prop.get_by_record(pay_prop)
                    if not rec_account and not pay_account:
                        action = self.env.ref('account.action_account_config')
                        msg = _('Cannot find a chart of accounts for this company, You should configure it. \nPlease go to Account Configuration.')
                        raise RedirectWarning(msg, action.id, _('Go to the configuration panel'))

            if type in ('out_invoice', 'out_refund'):
                account_id = rec_account.id
                payment_term_id = p.property_payment_term.id
            else:
                account_id = pay_account.id
                payment_term_id = p.property_supplier_payment_term.id
            if p.credit_allow ==True:
                payment_type='credit'
            elif p.is_consignment==True:
                payment_type='consignment'
            else:
                payment_type='cash'
                payment_term_id = 1                
            fiscal_position = p.property_account_position.id
            bank_id = p.bank_ids and p.bank_ids[0].id or False
            pricelist = p.property_product_pricelist and p.property_product_pricelist.id or False
            code=p.customer_code
            street= p.street
            street2=p.street2
            city=p.city and p.city.id or False
            state_id= p.state_id and p.state_id.id or False
            country_id=p.country_id and p.country_id.id or False
            township= p.township and p.township.id or False
        result = {'value': {
            'account_id': account_id,
            'payment_term': payment_term_id,
            'fiscal_position': fiscal_position,
            'payment_type':payment_type,
            'code':code,
            'street': street,
            'street2': street2,
            'city': city ,
            'state_id': state_id,
            'country_id': country_id ,
            'township': township,
            'pricelist_id':pricelist,
        }}

        if type in ('in_invoice', 'in_refund'):
            result['value']['partner_bank_id'] = bank_id

        if payment_term != payment_term_id:
            if payment_term_id:
                to_update = self.onchange_payment_term_date_invoice(payment_term_id, date_invoice)
                result['value'].update(to_update.get('value', {}))
            else:
                result['value']['date_due'] = False

        if partner_bank_id != bank_id:
            to_update = self.onchange_partner_bank(bank_id)
            result['value'].update(to_update.get('value', {}))
        return result        

    @api.model
    def _default_journal(self):
        inv_type = self._context.get('type', 'out_invoice')
        inv_types = inv_type if isinstance(inv_type, list) else [inv_type]
        company_id = self._context.get('company_id', self.env.user.company_id.id)
        payment_type=self.payment_type
        if (payment_type=='cash'):
            domain = [
                ('type', 'in', filter(None, map(TYPE2JOURNAL.get, inv_types))),
                ('direct_cash_sale','=',True),
                ('company_id', '=', company_id),
            ]
        elif (payment_type=='credit'):
            domain = [
                ('type', 'in', filter(None, map(TYPE2JOURNAL.get, inv_types))),
                ('credit_journal','=',True),                
                ('company_id', '=', company_id),
            ]
        else:         
            domain = [
                ('type', 'in', filter(None, map(TYPE2JOURNAL.get, inv_types))),
                ('company_id', '=', company_id),
            ]            
        return self.env['account.journal'].search(domain, limit=1)
    
#     state = fields.Selection([
#                     ('draft','Draft'),
#                     ('proforma','Pro-forma'),
#                     ('proforma2','Pro-forma'),
#                     ('fm_approve','Finance Manager Approved'),
#                     ('open','Cashier Approved'),
#                     ('paid','Paid'),
#                     ('cancel','Cancelled'),
#                 ], string='Status', index=True, readonly=True, default='draft',
#                 track_visibility='onchange', copy=False,
#                 help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
#                      " * The 'Pro-forma' when invoice is in Pro-forma status,invoice does not have an invoice number.\n"
#                      " * The 'Open' status is used when user create invoice,a invoice number is generated.Its in open status till user does not pay invoice.\n"
#                      " * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"
#                      " * The 'Cancelled' status is used when user cancel invoice.")
    payment_type = fields.Selection([
                    ('credit', 'Credit'),
                    ('cash', 'Cash'),
               #     ('consignment', 'Consignment'),
#                     ('advanced', 'Advanced')
                    ],string= 'Payment Type',default='cash')
    

    
    account_id = fields.Many2one('account.account', string='Account',
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        help="The partner account used for this invoice.")
    
    def finance_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'fm_approve'}, context=None)
        return True   
    
#     @api.multi    
#     def invoice_validate(self):    
#         payment_type = self.payment_type
#         if payment_type =='cash':
#             return self.write({'state': 'paid'})
#         else:    
#             return self.write({'state': 'open'})

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
                inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            date_invoice = inv.date_invoice

            company_currency = inv.company_id.currency_id
            # create the analytical lines, one move line per invoice line
            iml = inv._get_analytic_lines()
            # check if taxes are all computed
            compute_taxes = account_invoice_tax.compute(inv.with_context(lang=inv.partner_id.lang))
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
                    'ref': ref
                })

            date = date_invoice

            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)

            line = [(0, 0, self.line_get_convert(l, part.id, date)) for l in iml]
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
                'branch_id': inv.branch_id.id,
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
            move = account_move.with_context(ctx_nolang).create(move_vals)
            self.env.cr.execute('update account_move_line set branch_id=%s where move_id =%s ', (inv.branch_id.id ,move.id,))
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'period_id': period.id,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
        self._log_event()
        return True
