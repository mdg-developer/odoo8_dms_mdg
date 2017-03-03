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
        """Update the registry when a new rule is created."""
        if vals.get('partner_id'):
                partner_id=vals['partner_id']
                part = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)    
                defaults=self.onchange_partner_id(cr, uid, [], 'out_invoice', partner_id)['value']
                vals = dict(defaults, **vals)
        res_id = super(account_invoice, self).create(
            cr, uid, vals, context=context)

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
        print ' _default_journal'
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